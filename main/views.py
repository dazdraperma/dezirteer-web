import datetime
import time
from functools import partial
from io import StringIO
from multiprocessing import Pool

import numpy as np
import pandas as pd
from bokeh.embed import components
from bokeh.layouts import layout
from bokeh.models import Range1d, Span, Label
from bokeh.plotting import figure
from bokeh.resources import CDN
from crispy_forms.utils import render_crispy_form
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django_downloadview import VirtualDownloadView, VirtualFile
from scipy import stats

import main.const as const
from main import gui_support, fsutil, math_module
from main.forms import SettingsForm, UploadFileSessionForm, UploadFileForm
from .gui_support import *
from .import_export import *
import pandas_bokeh
import holoviews as hv
hv.extension('bokeh')
# renderer = hv.renderer('bokeh').instance(mode='server')

logger = logging.getLogger('views_log')


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None,
    )


def new_session(request):
    list_of_keys = list(request.session.keys())
    for key in list_of_keys:
        del request.session[key]

    response = HttpResponseRedirect('/')
    response.delete_cookie('keep_prev_data')

    return response


def get_keep_prev_data(request):
    if request.method == 'POST':
        keep_prev_data = request.POST.get('keep_prev_data')

        if 'gvars' in request.session:
            gvars = read_gvars(request)
            if keep_prev_data is not None:
                keep_prev = int(keep_prev_data)
            else:
                keep_prev = 0
            gvars['keep_prev_data'] = keep_prev
            write_gvars(request, gvars)

        response = JsonResponse({'msg': 'Success!'})
        set_cookie(response, 'keep_prev_data', keep_prev_data)

        return response

    return JsonResponse({'msg': ''})


def model_form_upload(request):
    if request.method == 'POST':
        gvars = read_gvars(request)

        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = handle_uploaded_file(request.FILES['file'])

            gvars['uploaded_file'] = uploaded_file['name'].split('.')[0]

            open_and_load_file(request, uploaded_file['path'], gvars)

            write_gvars(request, gvars)

            fsutil.remove_file(uploaded_file['path'])

            prev_data_av = gvars['g_grainset'] != []
            msg = '<div class="alert alert-success"><strong>Success!</strong> File successfully uploaded.</div>'
            return JsonResponse(
                {
                    'msg': msg,
                    'dc_table': gvars['pars_onChange'][1],
                    'samples': gvars['samples'],
                    'resp_gvars': gvars['form_values'],
                    'filename': uploaded_file['name'],
                    'status_text': gvars['status'][0],
                    'status_alert': gvars['status'][1],
                    'prev_data_av': prev_data_av
                }

            )
    else:

        form = UploadFileForm()

    context = {'form': form}
    html_form = render_to_string('main/model_form_upload.html', context, request=request)
    return JsonResponse({'html_form': html_form})


def handle_uploaded_file(f):
    x = datetime.datetime.now()
    path = settings.MEDIA_ROOT + '/documents/' + x.strftime("%Y/%m/%d/") + f.name
    from main.fsutil import make_dirs_for_file
    make_dirs_for_file(path)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    file = {'path': path, 'name': f.name}
    return file


def session_form_upload(request):
    if request.method == 'POST':
        form = UploadFileSessionForm(request.POST, request.FILES)
        if form.is_valid():
            loaded_object = handle_uploaded_session(request.FILES['file'])

            if str(loaded_object[5]) == 'web':
                gvars = loaded_object[4]  # web
            else:
                gvars = const.gvars_const

                gvars['g_grainset'] = loaded_object[0]
                gvars['g_graph_settings'] = loaded_object[1]
                gvars['g_filters'] = loaded_object[2]

                an_set = gvars['g_grainset'].analyses_list
                set_sample_names = set([split_name(l.analysis_name.split("_")) for l in an_set])

                set_ui_values(gvars, loaded_object[3])
                gvars['samples'] = tuple((s, s) for s in set_sample_names)
                # gvars['form_values']['lboxSamples'] = gvars['samples']

                gvars['g_list_of_samples'] = same_sample_set(gvars['g_grainset'])

                gvars['g_table'] = []

                gvars['pars_onChange'] = [gvars['g_filters'], gvars['g_table'], gvars['g_grainset'], gvars['g_list_col_names']]

            fill_data_table(gvars, gvars['pars_onChange'][1], gvars['pars_onChange'][2], gvars['pars_onChange'][0],
                            gvars['pars_onChange'][3])

            write_gvars(request, gvars)

            msg = '<div class="alert alert-success"><strong>Success!</strong> Session successfully uploaded.</div>'
            return JsonResponse(
                {
                    'msg': msg,
                    'dc_table': gvars['pars_onChange'][1],
                    'samples': gvars['samples'],
                    'resp_gvars': gvars['form_values'],
                    'platform': str(loaded_object[5])
                }
            )
    else:
        form = UploadFileSessionForm()
    context = {'form': form}
    html_form = render_to_string('main/session_form_upload.html', context, request=request)
    return JsonResponse({'html_form': html_form})


def handle_uploaded_session(f):
    sys.modules['math_module'] = math_module
    sys.modules['gui_support'] = gui_support
    x = datetime.datetime.now()
    path = settings.MEDIA_ROOT + '/documents/' + x.strftime("%Y/%m/%d/") + f.name
    from main.fsutil import make_dirs_for_file, read_file
    make_dirs_for_file(path)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    content_file = read_file(path)
    obj_file = pickle.loads(bytes.fromhex(content_file))
    return obj_file


def get_checkboxes(gvars, p_value, key):
    if (type(p_value) is str) and (str(p_value) == 'on'):
        value = 1
    else:
        value = 0

    if key == 'chbShowCalc':
        gvars['varShowCalc'] = value
    elif key == 'chbKeepPrev':
        gvars['varKeepPrev'] = value
    elif key == 'chbLimitAgeSpectrum':
        gvars['varLimitAgeSpectrum'] = value
    elif key == 'chbIncludeBadEllipses':
        gvars['varIncludeBadEllipses'] = value
    elif key == 'chbInclude207235Err':
        gvars['varInclude207235Err'] = value
    elif key == 'chbShowErrorBars':
        gvars['varShowErrorBars'] = value
    elif key == 'chbShowEllipses':
        gvars['varShowEllipses'] = value
        if value == 0:
            gvars['varIncludeBadEllipses'] = 0
            gvars['varShowErrorBars'] = 1


def set_checkbox(gvars, value, key):
    if int(value) == 1:
        gvars['form_values'][key] = 'on'


def set_ui_elements(gvars):
    form = SettingsForm(initial=gvars['form_values'])
    for key, val in gvars['form_values'].items():
        get_checkboxes(gvars, val, key)

    return form


def get_ui_values(gvars):
    gui_elements = []
    gui_elements.append(gvars['lbShowStatus'])  # 0
    gui_elements.append(gvars['varUncType'])  # 1
    gui_elements.append(gvars['form_values']['cbWhichAge'])  # 2
    gui_elements.append(gvars['form_values']['entAgeCutoff'])  # 3
    gui_elements.append(gvars['form_values']['cbPbc'])  # 4
    gui_elements.append(gvars['form_values']['cbWhichConc'])  # 5
    gui_elements.append(gvars['form_values']['entDiscAgeFixedLim'])  # 6
    gui_elements.append(gvars['form_values']['entNegDiscFilt'])  # 7
    gui_elements.append(gvars['form_values']['entPosDiscFilt'])  # 8
    gui_elements.append(gvars['form_values']['cbErrFilter'])  # 9
    gui_elements.append(gvars['form_values']['entErrFilter'])  # 10
    gui_elements.append(gvars['varInclude207235Err'])  # 11
    gui_elements.append(gvars['form_values']['entUconcCutoff'])  # 12
    gui_elements.append(gvars['form_values']['cbUConc'])  # 13
    gui_elements.append(gvars['form_values']['cbConcType'])  # 14
    gui_elements.append(gvars['form_values']['cbEllipsesAt'])  # 15
    gui_elements.append(gvars['form_values']['cbDensityPlotType'])  # 16
    gui_elements.append(gvars['form_values']['entHistBinwidth'])  # 17
    gui_elements.append(gvars['form_values']['entKDEBandwidth'])  # 18
    gui_elements.append(gvars['form_values']['entAgeMinCrop'])  # 19
    gui_elements.append(gvars['varMinAgeCrop'])  # 20
    gui_elements.append(gvars['form_values']['entAgeMaxCrop'])  # 21
    gui_elements.append(gvars['varShowCalc'])  # 22
    gui_elements.append(gvars['varKeepPrev'])  # 23
    gui_elements.append(gvars['varMaxAgeCrop'])  # 24
    gui_elements.append(gvars['samples'])  # 25
    gui_elements.append(gvars['varLimitAgeSpectrum'])  # 26
    gui_elements.append(gvars['lbShowStatus'])  # 27
    gui_elements.append(gvars['varDiscPerc'])  # 28
    gui_elements.append(gvars['form_values']['cbDiscIntersect'])  # 29
    gui_elements.append(gvars['form_values']['cbShowUncorrCorrBothEllipses'])  # 30
    gui_elements.append(gvars['varIncludeBadEllipses'])  # 31
    gui_elements.append(gvars['form_values']['lboxSamples'])  # 32
    # for the web version
    gui_elements.append(gvars['form_values']['cbWhichAge'])  # 33 (2)
    gui_elements.append(gvars['form_values']['cbPbc'])  # 34 (4)
    gui_elements.append(gvars['form_values']['cbWhichConc'])  # 35 (5)
    gui_elements.append(gvars['form_values']['cbErrFilter'])  # 36 (9)
    gui_elements.append(gvars['form_values']['cbUConc'])  # 37 (13)
    gui_elements.append(gvars['form_values']['cbConcType'])  # 38 (14)
    gui_elements.append(gvars['form_values']['cbEllipsesAt'])  # 39 (15)
    gui_elements.append(gvars['form_values']['cbDensityPlotType'])  # 40 (16)
    gui_elements.append(gvars['form_values']['cbDiscIntersect'])  # 41 (29)
    gui_elements.append(gvars['form_values']['cbShowUncorrCorrBothEllipses'])  # 42 (30)
    gui_elements.append(gvars['form_values']['chbShowErrorBars'])  # 43
    gui_elements.append(gvars['form_values']['chbShowEllipses'])  # 44


    return gui_elements


def set_ui_values(gvars, args):
    # self.enable_all_ui_elements()

    gvars['lbShowStatus'] = args[0]
    gvars['varUncType'] = args[1]
    gvars['form_values']['uncType'] = args[1]
    gvars['form_values']['cbWhichAge'] = args[33]
    gvars['form_values']['entAgeCutoff'] = args[3]
    gvars['form_values']['cbPbc'] = args[34]
    gvars['form_values']['cbWhichConc'] = args[35]
    gvars['form_values']['entDiscAgeFixedLim'] = args[6]
    gvars['form_values']['entNegDiscFilt'] = args[7]
    gvars['form_values']['entPosDiscFilt'] = args[8]
    gvars['form_values']['cbErrFilter'] = args[36]
    gvars['form_values']['entErrFilter'] = args[10]
    gvars['varInclude207235Err'] = args[11]
    set_checkbox(gvars, args[11], 'chbInclude207235Err')
    gvars['form_values']['entUconcCutoff'] = args[12]
    gvars['form_values']['cbUConc'] = args[37]
    gvars['form_values']['cbConcType'] = args[38]
    gvars['form_values']['cbEllipsesAt'] = args[39]
    gvars['form_values']['cbDensityPlotType'] = args[40]
    gvars['form_values']['entHistBinwidth'] = args[17]
    gvars['form_values']['entKDEBandwidth'] = args[18]
    gvars['varMinAgeCrop'] = args[20]
    set_checkbox(gvars, args[20], 'chbMinAgeCrop')
    gvars['varMaxAgeCrop'] = args[24]
    set_checkbox(gvars, args[24], 'chbMaxAgeCrop')
    gvars['form_values']['entAgeMinCrop'] = args[19]
    gvars['form_values']['entAgeMaxCrop'] = args[21]
    gvars['varShowCalc'] = args[22]
    set_checkbox(gvars, args[22], 'chbShowCalc')
    gvars['varKeepPrev'] = args[23]
    set_checkbox(gvars, args[23], 'chbKeepPrev')
    gvars['samples'] = args[25]
    gvars['varLimitAgeSpectrum'] = args[26]
    set_checkbox(gvars, args[26], 'chbLimitAgeSpectrum')
    gvars['lbShowStatus'] = args[27]
    gvars['varDiscPerc'] = args[28]
    gvars['form_values']['rbDiscPerc'] = args[28]
    gvars['form_values']['cbDiscIntersect'] = args[41]
    gvars['form_values']['cbShowUncorrCorrBothEllipses'] = args[42]
    gvars['varIncludeBadEllipses'] = args[31],
    set_checkbox(gvars, args[31], 'chbIncludeBadEllipses')
    gvars['form_values']['lboxSamples'] = args[32]
    gvars['varShowErrorBars'] = args[43]
    set_checkbox(gvars, args[43], 'chbShowErrorBars')
    gvars['varShowEllipses'] = args[44]
    set_checkbox(gvars, args[44], 'chbShowEllipses')


class StringIODownloadView(VirtualDownloadView):
    def get_file(self):
        x = datetime.datetime.now()
        pack_gvars = self.request.session['gvars']
        gvars = pickle.loads(bytes.fromhex(pack_gvars))
        l_ui_values = get_ui_values(gvars)
        object_to_save = [gvars['g_grainset'], gvars['g_graph_settings'], gvars['g_filters'], l_ui_values, gvars, 'web']
        pack_object = pickle.dumps(object_to_save, pickle.HIGHEST_PROTOCOL).hex()

        file_obj = StringIO(pack_object)

        return VirtualFile(file_obj, name="work_session_" + x.strftime("%Y%m%d%H%M%S") + ".dzr")


def write_gvars(request, val):
    request.session['gvars'] = pickle.dumps(val, pickle.HIGHEST_PROTOCOL).hex()


def read_gvars(request):
    return pickle.loads(bytes.fromhex(request.session['gvars']))


def truncate(f, n):
    return floor(f * 10 ** n) / 10 ** n


def set_pval_dval(gvars):
    if gvars['g_prev_cum'] == []:
        pval = 0
        dval = 0
    else:
        if int(gvars['g_graph_settings'].pdp_kde_hist) == 0:
            curr_cum = gvars['g_ckde']

        elif int(gvars['g_graph_settings'].pdp_kde_hist) == 1:
            curr_cum = gvars['g_cpdp']

        else:
            curr_cum = []
        dval = d_value(curr_cum, gvars['g_prev_cum'])
        pval = p_value(dval, gvars['g_number_of_good_grains'][0], gvars['g_prev_n'][0])

    if not gvars['g_prev_prob']:
        like = 0
        sim = 0
    else:
        if int(gvars['g_graph_settings'].pdp_kde_hist) == 0:
            curr_prob = gvars['g_kde']
        elif int(gvars['g_graph_settings'].pdp_kde_hist) == 1:
            curr_prob = gvars['g_pdp']
        else:
            curr_prob = []

        like = likeness(curr_prob, gvars['g_prev_prob'])
        sim = similarity(curr_prob, gvars['g_prev_prob'])
    gvars['g_pval_dval'] = [pval, dval, like, sim]
    return gvars


def peaks(gvars):
    if int(gvars['g_graph_settings'].pdp_kde_hist) == 0 and len(gvars['g_kde']) > 0:
        return gvars['g_kde'][1]
    elif int(gvars['g_graph_settings'].pdp_kde_hist) == 0 and len(gvars['g_pdp']) > 0:
        return gvars['g_pdp'][1]


def reset_controls(gvars, is_data_present):
    if is_data_present:

        if gvars['samples'] == '':
            status_text = ' data, bad divider'
            status_color = 'text-danger'
        else:
            status_text = '  data OK'
            status_color = 'text-success'
        gvars['status'] = [gvars['g_file_type'] + status_text, status_color]
    else:

        gvars['samples'] = []
        gvars['status'] = ["No Data", "text-danger"]
        gvars['g_table'] = []
    gvars['g_plot_txt'] = ''


def split_name(name):
    n = ''
    for i in range(len(name) - 1):
        n += name[i]
        if i < len(name) - 2:
            n += '_'
    return n


def open_and_load_file(request, user_file, gvars):
    try:
        if gvars['g_plot_txt'] != "":
            gvars['g_plot_txt'] = ""
        # keep_prev = 0
        # keep_prev_data_c = request.COOKIES.get('keep_prev_data')
        # if keep_prev_data_c is not None:
        #     keep_prev = keep_prev_data_c

        keep_prev = gvars['keep_prev_data']

        gvars['g_filters'].sample_name_filter = []
        use_pbc = gvars['varMinAgeCrop'] == 1

        if user_file != '':

            an_set = []

            start_0 = time.time()

            file = imported_file(user_file)

            end_0 = time.time()
            print("imported_file: " + str(end_0 - start_0))

            gvars['g_file_type'] = file[1]

            start_1 = time.time()
            # multithreading
            iterable = list(range(1, file[2]))
            pool = Pool()
            func = partial(file_to_analysis, file)
            an_set = pool.map(func, iterable)
            pool.close()
            pool.join()

            end_1 = time.time()
            print("file_to_analysis: " + str(end_1 - start_1))

            if int(keep_prev) == 1:
                grainset = gvars['g_grainset']
                an_set = an_set + grainset.analyses_list

            start_1 = time.time()

            grainset = AnalysesSet(an_set, 'set#1')
            grainset.good_bad_sets(gvars['g_filters'])

            end_1 = time.time()
            print("AnalysesSet and good_bad_sets: " + str(end_1 - start_1))

            gvars['g_table'] = []

            gvars['pars_onChange'] = [gvars['g_filters'], gvars['g_table'], grainset, gvars['g_list_col_names']]

            fill_data_table(gvars, gvars['g_table'], grainset, gvars['g_filters'],
                                  gvars['g_list_col_names'])

            gvars['g_list_of_samples'] = same_sample_set(grainset)

            set_sample_names = set([split_name(l.analysis_name.split("_")) for l in an_set])
            gvars['samples'] = tuple((s, s) for s in set_sample_names)

            gvars['g_grainset'] = grainset
            reset_controls(gvars, True)
        else:
            pass

    except ValueError:
        reset_controls(gvars, False)
        # gvars['status'] = [gvars['g_file_type'] + " data problem\nbetween grains #{}\nand #{}".
        #     format(file_to_analysis(file, i - 1), file_to_analysis(file, i + 1)), 'red']
    return gvars


def concordia_type(gvars):
    if int(gvars['g_graph_settings'].conc_type) == 0:
        conc_graph_x = [i[1] for i in gvars['concordia_table']]
        conc_graph_y = [i[0] for i in gvars['concordia_table']]
        conc_title = "Conventional Concordia"
        conc_graph_xtitle = "207/235"
        conc_graph_ytitle = "206/238"
        xconc = 1
        yconc = 0
    else:
        conc_graph_x = [(1 / i[0]) for i in gvars['concordia_table']]
        conc_graph_y = [i[2] for i in gvars['concordia_table']]
        conc_title = "Tera-Wasserburg Concordia"
        conc_graph_xtitle = "238/206"
        conc_graph_ytitle = "207/206"
        xconc = 3
        yconc = 2
    '''else: 
            
            conc_graph_x = [(1 / i[0]) for i in concordia_table]
            
            conc_graph_y = [i[2] for i in concordia_table]
            
            conc_title = "ln Tera-Wasserburg Concordia"
            conc_graph_xtitle = "ln(238/206)"
            conc_graph_ytitle = "ln(207/206)"
            xconc = 3
            yconc = 2'''
    return [conc_graph_x, conc_graph_y, conc_title, conc_graph_xtitle, conc_graph_ytitle, xconc, yconc]


def min_max_ages(request, gvars, grainset):

    if int(gvars['varLimitAgeSpectrum']) == 1:
        min_age = grainset.min_age
        max_age = grainset.max_age
        '''min_age = g_number_of_good_grains[6]
        max_age = g_number_of_good_grains[5]'''

        if int(gvars['g_graph_settings'].conc_type) == 0:
            min_conc_x = grainset.min_207_235
            max_conc_x = grainset.max_207_235

            min_conc_y = grainset.min_206_238
            max_conc_y = grainset.max_206_238
        else:
            min_conc_x = grainset.min_238_206
            max_conc_x = grainset.max_238_206

            min_conc_y = grainset.min_207_206
            max_conc_y = grainset.max_207_206

    else:
        min_age = 0
        max_age = EarthAge
        min_conc_x = 0
        min_conc_y = 0
        if int(gvars['g_graph_settings'].conc_type) == 0:
            max_conc_x = 100
            max_conc_y = 1.1
        else:
            max_conc_x = 60
            max_conc_y = 0.7
    return [min_age, max_age, min_conc_x, max_conc_x, min_conc_y, max_conc_y]


def clear_graph(gvars):
    gvars['g_prev_n'] = 0
    gvars['g_prev_cum'] = []
    gvars['g_prev_prob'] = []

    gvars['g_plot_txt'] = ""


def clear_prev_or_remove_text(request, gvars):
    if gvars['varKeepPrev'] == 0:
        clear_graph(gvars)
    else:
        if gvars['g_plot_txt'] != "":
            gvars['g_plot_txt'] = ""
    gvars['g_plot_txt'] = ""
    return gvars


def kde_pdp_hist(gvars, grainset):
    if gvars['g_graph_settings'].pdp_kde_hist == 0:
        gvars['g_prob_graph_to_draw'] = gvars['g_kde'][0]
        gvars['g_cum_graph_to_draw'] = gvars['g_kde'][2]
        gvars['g_prob_title'] = "Kernel Density Estimates (KDE)"
        gvars['g_cum_title'] = "Cumulative KDE"
    elif int(gvars['g_graph_settings'].pdp_kde_hist) == 1:
        gvars['g_prob_graph_to_draw'] = gvars['g_pdp'][0]
        gvars['g_cum_graph_to_draw'] = gvars['g_cpdp']
        gvars['g_prob_title'] = "Probability Density Plot (PDP)"
        gvars['g_cum_title'] = "Cumulative PDP"
    else:
        tuple_list = sorted(list(grainset.good_set.values()), key=lambda x: x[0])
        gvars['g_prob_graph_to_draw'] = [x[0] for x in tuple_list]
        gvars['g_cum_graph_to_draw'] = []
        gvars['g_prob_title'] = "Histogram"
        gvars['g_cum_title'] = "Cumulative Histogram"
    return [gvars['g_prob_graph_to_draw'], gvars['g_cum_graph_to_draw'], gvars['g_prob_title'],
            gvars['g_cum_title']]


def set_plot_types_and_titles(request, gvars, kde_pdp_hist):
    gvars['g_prob_graph_to_draw'] = kde_pdp_hist[0]
    gvars['g_cum_graph_to_draw'] = kde_pdp_hist[1]
    gvars['g_prob_title'] = kde_pdp_hist[2]
    gvars['g_cum_title'] = kde_pdp_hist[3]
    return gvars


def plot_with_points(f, plot_x):
    return hv.Curve((plot_x, f(plot_x)))


def set_axes(request, gvars, conc_title, conc_graph_xtitle, conc_graph_ytitle, conc_graph_x, conc_graph_y, min_age,
             max_age,
             min_conc_x, max_conc_x, min_conc_y, max_conc_y):
    # set axis of all graphs
    gvars['graph_values']['ax_conc'].title.text = conc_title
    gvars['graph_values']['ax_conc'].xaxis.axis_label = conc_graph_xtitle
    gvars['graph_values']['ax_conc'].yaxis.axis_label = conc_graph_ytitle
    gvars['graph_values']['ax_prob'].title.text = gvars['g_prob_title']
    gvars['graph_values']['ax_prob'].xaxis.axis_label = 'Age (Ma)'
    gvars['graph_values']['ax_cum'].title.text = gvars['g_cum_title']
    gvars['graph_values']['ax_cum'].xaxis.axis_label = 'Age (Ma)'
    # delete Artem
    # gvars_a['graph_values']['ax_conc'].line(conc_graph_x, conc_graph_y, line_width=2)
    gvars['graph_values']['ax_conc'].x_range = Range1d(min_conc_x, max_conc_x)
    gvars['graph_values']['ax_conc'].y_range = Range1d(min_conc_y, max_conc_y)
    if gvars['g_graph_settings'].conc_type == 2:
        gvars['graph_values']['ax_conc'].axes.set_yscale("log")

    return gvars


def draw_concordia_ticks(request, gvars, xconc, yconc, min_age, max_age, min_conc_x, max_conc_x, min_conc_y, max_conc_y,
                         conc_title, conc_graph_xtitle, conc_graph_ytitle):

    if max_age - min_age > 1000:
        step = 500
    elif 500 < max_age - min_age < 1000:
        step = 250
    elif 100 < max_age - min_age < 500:
        step = 50
    elif 50 < max_age - min_age < 100:
        step = 25
    else:
        step = 10

    if log10(min_age) >= 2:
        x = -2
        x_l = -2
    else:
        x = -1
        x_l = -2

    t_val = []
    x_val = []
    y_val = []
    for t in range(int(truncate(min_age, x)), int(max_age) + step, step):
        if t == 0:
            t += 1
        x = calc_ratio(t)[xconc]
        y = calc_ratio(t)[yconc]
        if int(gvars['g_graph_settings'].conc_type) == 2:
            x = log(x)
            y = log(y)

        t_val.append(str(t))
        x_val.append(x)
        y_val.append(y)

    x_val_l = []
    y_val_l = []
    step_for_line = 1
    for t_l in range(int(truncate(min_age, x_l)), int(max_age) + step_for_line, step_for_line):
        if t_l == 0:
            t_l += 1
        x_l = calc_ratio(t_l)[xconc]
        y_l = calc_ratio(t_l)[yconc]
        if int(gvars['g_graph_settings'].conc_type) == 2:
            x_l = log(x_l)
            y_l = log(y_l)

        x_val_l.append(x_l)
        y_val_l.append(y_l)

    gvars['graph_values']['ax_conc'].line(x_val_l, y_val_l, line_width=2)
    gvars['graph_values']['ax_conc'].text(x_val, y_val, t_val, x_offset=5, y_offset=10, text_font_size='0.8em')
    gvars['graph_values']['ax_conc'].circle(x_val, y_val, fill_color="black", size=5)

    # scatter = hv.Scatter(list(zip(x_val, y_val)))
    # scatter.opts(color='black', size=5, marker='circle')
    # gvars['graph_values']['ax_conc_list'].append(scatter)
    #
    # labels = hv.Labels({('x', 'y'): list(zip(x_val, y_val)), 'text': t_val}, ['x', 'y'], 'text')
    # labels.opts(text_font_size='8pt')
    # gvars['graph_values']['ax_conc_list'].append(labels)
    #
    # curve = hv.Curve(list(zip(x_val_l, y_val_l)))
    # curve.opts(color='blue', xlim=(min_conc_x, max_conc_x), ylim=(min_conc_y, max_conc_y),
    #
    #            title=conc_title,
    #            xlabel=conc_graph_xtitle,
    #            ylabel=conc_graph_ytitle,
    #            )
    # gvars['graph_values']['ax_conc_list'].append(curve)

    return gvars


def draw_error_bars(fig, x, y, xerr=None, yerr=None, color='red',
             point_kwargs={}, error_kwargs={}):

  fig.circle(x, y, color=color, **point_kwargs)

  if xerr:
      x_err_x = []
      x_err_y = []
      for px, py, err in zip(x, y, xerr):
          x_err_x.append((px - err, px + err))
          x_err_y.append((py, py))
      fig.multi_line(x_err_x, x_err_y, color=color, **error_kwargs)

  if yerr:
      y_err_x = []
      y_err_y = []
      for px, py, err in zip(x, y, yerr):
          y_err_x.append((px, px))
          y_err_y.append((py - err, py + err))
      fig.multi_line(y_err_x, y_err_y, color=color, **error_kwargs)


def plot_conc_ellipses(request, gvars, grainset):
    current_set = [grainset.good_set, grainset.bad_set]
    which_ellipse_to_plot = int(gvars['form_values']['cbShowUncorrCorrBothEllipses'])

    if which_ellipse_to_plot == 2:
        j = 2
    else:
        j = 1

    # print('PLOT_BAD_ELLIPSE', gvars['varIncludeBadEllipses'])
    if type(gvars['varIncludeBadEllipses']) == tuple:  # bag ???
        gvars['varIncludeBadEllipses'] = gvars['varIncludeBadEllipses'][0]

    plot_bad_ellipses = int(gvars['varIncludeBadEllipses'])
    plot_error_bars = int(gvars['varShowErrorBars'])
    plot_ellipses = int(gvars['varShowEllipses'])

    list_ellipses = []
    list_points = []
    list_errorbars = []

    x_l = []
    y_l = []
    w_l = []
    h_l = []
    ang_l = []
    oval_color_l = []
    oval_fill_l = []
    line_style_l = []
    line_thickness_l = []

    x_err_l = []
    y_err_l = []

    for i in (0, 1):

        for k in range(0, j):

            for zir in current_set[i]:

                sigma_level = gvars['g_graph_settings'].ellipses_at
                if which_ellipse_to_plot == 0 or (which_ellipse_to_plot == 2 and k == 0):
                    corr_coef_75_68 = zir.corr_coef_75_68
                    corr_coef_86_76 = zir.corr_coef_86_76
                    pb207_u235 = zir.pb207_u235
                    pb206_u238 = zir.pb206_u238
                    u238_pb206 = zir.u238_pb206(False)
                    pb207_pb206 = zir.pb207_pb206
                    oval_color = "green"

                elif which_ellipse_to_plot == 1 or (which_ellipse_to_plot == 2 and k == 1):
                    corr_coef_75_68 = zir.corr_coef_75_68_204
                    corr_coef_86_76 = zir.corr_coef_86_76_204
                    pb207_u235 = zir.rat75_204corr
                    pb206_u238 = zir.rat68_204corr
                    u238_pb206 = zir.u238_pb206(True)
                    pb207_pb206 = zir.rat76_204corr
                    oval_color = "blue"
                # conventional concordia
                if int(gvars['g_graph_settings'].conc_type) == 0:
                    corr_coef = corr_coef_75_68
                    x_conc = pb207_u235[0]
                    y_conc = pb206_u238[0]
                    x_err = pb207_u235[int(gvars['varUncType'])]
                    y_err = pb206_u238[int(gvars['varUncType'])]
                # Tera-Wasserburg concordia
                else:
                    corr_coef = corr_coef_86_76
                    x_conc = u238_pb206[0]
                    x_err = u238_pb206[int(gvars['varUncType'])]
                    y_conc = pb207_pb206[0]
                    y_err = pb207_pb206[int(gvars['varUncType'])]
                '''else: 
                    if u238_pb206[0]>0 and pb207_pb206[0]>0:
                        corr_coef = corr_coef_86_76
                        x_conc = log(u238_pb206[0])
                        x_err = 0.434*(u238_pb206[gui_support.varUncType.get()])/(u238_pb206[0])
                        y_conc = (pb207_pb206[0])
                        y_err = 0.434*(pb207_pb206[gui_support.varUncType.get()])/(pb207_pb206[0])
                    else:
                        shall_plot = False'''

                if (x_conc > 0) and (x_err > 0) and (y_conc > 0) and (y_err > 0):
                    a1 = x_err * corr_coef * sqrt(2) * sigma_level
                    a2 = y_err * corr_coef * sqrt(2) * sigma_level
                    ang = atan(tan(2 * (atan(a2 / a1))) * corr_coef) / 2
                    chi_sq_fact = stats.chi2.ppf(conf_lim(sigma_level), 2)
                    c1 = 2 * (1 - corr_coef ** 2) * chi_sq_fact
                    c2 = 1 / cos(2 * ang)
                    vx = x_err ** 2
                    vy = y_err ** 2
                    test_major_axis = c1 / ((1 + c2) / vx + (1 - c2) / vy)
                    a = sqrt(test_major_axis)
                    test_minor_axis = c1 / ((1 - c2) / vx + (1 + c2) / vy)
                    b = sqrt(test_minor_axis)

                    if i == 1:
                        if plot_bad_ellipses == 1 and ((parse_sample_analysis(zir.analysis_name)[
                                                            0] in gvars['g_filters'].sample_name_filter) or gvars[
                                                           'g_filters'].sample_name_filter == []):
                            shall_plot = True
                            line_thickness = 1
                            line_style = 'dotted'
                        else:
                            shall_plot = False
                            line_style = 'solid'

                    else:
                        shall_plot = True
                        line_thickness = 1
                        line_style = 'solid'

                    if shall_plot:
                        x_l.append(x_conc)
                        y_l.append(y_conc)
                        w_l.append(a * 2)
                        h_l.append(b * 2)
                        ang_l.append(degrees(ang))
                        oval_color_l.append(oval_color)
                        # oval_fill_l.append(oval_fill)
                        line_style_l.append(line_style)
                        line_thickness_l.append(line_thickness)

                        x_err_l.append(x_err * sigma_level)
                        y_err_l.append(y_err * sigma_level)

                        if plot_ellipses == 1:
                            ellipse = hv.Ellipse(x_conc, y_conc, (a * 2, b * 2), orientation=ang)
                            ellipse.opts(aspect='square', color=oval_color, line_dash=line_style)

                            list_ellipses.append(ellipse)

    if plot_error_bars == 1:
        draw_error_bars(gvars['graph_values']['ax_conc'], x_l, y_l, x_err_l, y_err_l)

    gvars['graph_values']['ax_conc_list'] = list_ellipses


def plot_peaks(request, gvars, min_age, max_age, grainset):
    gvars['g_prob_graph_to_draw'] = kde_pdp_hist(gvars, grainset)[0]

    l_min_age = min_age
    l_max_age = max_age

    if l_min_age % 2 != 0:
        l_min_age -= 1

    if l_max_age % 2 != 0:
        l_max_age -= 1

    range_of_ages = range(l_min_age, l_max_age, 2)

    curve = hv.Curve((list(range_of_ages), gvars['g_prob_graph_to_draw'][l_min_age // 2: l_max_age // 2]))
    curve.opts(line_width=2, title=gvars['g_prob_title'], xlabel='Age (Ma)', line_color='green')

    gvars['graph_values']['ax_prob_list'].append(curve)

    if gvars['varShowCalc'] == 1:
        i = 0

        gvars['graph_values']['ax_prob'].title.text = gvars['g_prob_title']

        if int(gvars['g_graph_settings'].pdp_kde_hist) == 0:
            list_peaks = gvars['g_kde'][1]
        elif int(gvars['g_graph_settings'].pdp_kde_hist) == 1:
            list_peaks = gvars['g_pdp'][1]
        else:
            list_peaks = []
        while i < len(list_peaks):

            vline = hv.VLine(list_peaks[i])
            vline.opts(line_width=0.5, line_color='red', line_dash='dashed')
            # gvars['graph_values']['ax_prob'] *= vline
            gvars['graph_values']['ax_prob_list'].append(vline)

            i += 1


def plot_text(request, gvars, pval, dval):
    # varShowCalc = 0
    # if 'varShowCalc' in request.session:
    #     varShowCalc = read_var(request, 'varShowCalc')
    #
    # if (varShowCalc == 1) or (gvars['varShowCalc'] == 1):
    if gvars['varShowCalc'] == 1:
        text_to_show = list()
        text_to_show.append("n=" + str(gvars['g_number_of_good_grains'][0]) + "\n")
        text_to_show.append("Min age=" + str(int(gvars['g_number_of_good_grains'][6])) + "; " + "Max age=" + str(
            int(gvars['g_number_of_good_grains'][5])) + "\n")
        text_to_show.append("WA age=" + str(round((gvars['g_number_of_good_grains'][1]), 1)) + "+-" + str(
            2 * round((gvars['g_number_of_good_grains'][2]), 1)) + "(2σ int.);\n")
        text_to_show.append("+-" + str(round((gvars['g_number_of_good_grains'][3]), 1)) + "(95%conf)\n")
        text_to_show.append("MSWD=" + str(round(gvars['g_number_of_good_grains'][4], 2)) + "\n")
        text_to_show.append("KS p-value=" + str(round(pval, 2)) + "; " + "d-value=" + str(round(dval, 2)) + "\n")
        text_to_show.append("Likeness=" + str(round(gvars['g_pval_dval'][2], 2)) + "\n")
        text_to_show.append("Similarity=" + str(round(gvars['g_pval_dval'][3], 2)) + "\n")

        txt_teaks_at = "peaks at "
        i = 1
        for p in peaks(gvars):
            if len(peaks(gvars)) > 10 and i == 10:
                txt_teaks_at += "\n (for more peaks click STATISTICS)"
                break
            if i < len(peaks(gvars)):
                txt_teaks_at += str(p) + ", "
            else:
                txt_teaks_at += str(p)
            if i % 5 == 0 and i < len(peaks(gvars)):
                txt_teaks_at += "\n    "
            i += 1

        text_to_show.append(txt_teaks_at)

    else:
        if gvars['g_plot_txt'] != "":
            gvars['g_plot_txt'] = ""
        text_to_show = []

    txt_show = ''
    for t in text_to_show:
        txt_show += t

    text_stat = hv.Text(60, 0.3, txt_show, fontsize=10, halign='left', valign='center')
    # gvars['graph_values']['ax_cum'] *= text_stat
    gvars['graph_values']['ax_cum_list'].append(text_stat)

    citation = Label(x=100, y=100, text="Green: uncorr.", x_units='screen', y_units='screen',
                     text_font_size='1em', text_color='green', render_mode='css',
                     border_line_color='black', border_line_alpha=0.0,
                     background_fill_color='white', background_fill_alpha=0.0)
    gvars['graph_values']['ax_conc'].add_layout(citation)

    citation = Label(x=100, y=80, text="Blue: 204Pbc", x_units='screen', y_units='screen',
                     text_font_size='1em', text_color='blue', render_mode='css',
                     border_line_color='black', border_line_alpha=0.0,
                     background_fill_color='white', background_fill_alpha=0.0)
    gvars['graph_values']['ax_conc'].add_layout(citation)

    citation = Label(x=100, y=60, text="Dotted: bad", x_units='screen', y_units='screen',
                     text_font_size='1em', text_color='black', render_mode='css',
                     border_line_color='black', border_line_alpha=0.0,
                     background_fill_color='white', background_fill_alpha=0.0)
    gvars['graph_values']['ax_conc'].add_layout(citation)

    citation = Label(x=100, y=40, text="Red: errors", x_units='screen', y_units='screen',
                     text_font_size='1em', text_color='red', render_mode='css',
                     border_line_color='black', border_line_alpha=0.0,
                     background_fill_color='white', background_fill_alpha=0.0)
    gvars['graph_values']['ax_conc'].add_layout(citation)

    # text_cit = hv.Text(60, 0.3, 'Green:uncorr.\n Blue:204Pbc \n Dotted:bad', fontsize=10, halign='left',
    #                    valign='center')
    # # gvars['graph_values']['ax_conc'] *= text_cit
    # gvars['graph_values']['ax_conc_list'].append(text_cit)

    if int(gvars['g_graph_settings'].pdp_kde_hist) != 2:
        minmax_ages = min_max_ages(request, gvars, gvars['g_grainset'])
        plot_peaks(request, gvars, minmax_ages[0], minmax_ages[1], gvars['g_grainset'])


def plot_conc_text_peaks(request, gvarsctp, min_age, max_age):
    plot_text(request, gvarsctp, gvarsctp['g_pval_dval'][0], gvarsctp['g_pval_dval'][1])

    gvarsctp['g_prev_n'] = gvarsctp['g_number_of_good_grains']
    if int(gvarsctp['g_graph_settings'].pdp_kde_hist) == 0:
        gvarsctp['g_prev_cum'] = gvarsctp['g_ckde']
        gvarsctp['g_prev_prob'] = gvarsctp['g_kde']
    else:
        gvarsctp['g_prev_cum'] = gvarsctp['g_cpdp']
        gvarsctp['g_prev_prob'] = gvarsctp['g_pdp']

    return gvarsctp


def prob_cum_plot(request, gvars, min_age, max_age, grainset):
    from bokeh.palettes import Dark2_5 as palette
    import itertools
    colors = itertools.cycle(palette)

    l_min_age = min_age
    l_max_age = max_age

    if l_min_age % 2 != 0:
        l_min_age -= 1

    if l_max_age % 2 != 0:
        l_max_age -= 1
    range_of_ages = range(l_min_age, l_max_age, 2)

    data = dict(x=list(range_of_ages), y=gvars['g_cum_graph_to_draw'][l_min_age // 2: l_max_age // 2])

    if int(gvars['varKeepPrev']) == 1:

        gvars['list_data_glifs'].append(data)

        for data_glif in gvars['list_data_glifs']:
            curve = hv.Curve(list(zip(data_glif['x'], data_glif['y'])))
            curve.options(line_width=2, line_alpha=0.6, color=next(colors))
            gvars['graph_values']['ax_cum_list'].append(curve)


    else:
        gvars['list_data_glifs'] = []

        curve = hv.Curve(list(zip(data['x'], data['y'])))
        curve.options(line_width=2, line_alpha=0.6, color=next(colors))

        gvars['graph_values']['ax_cum_list'].append(curve)

    gvars = plot_peaks(request, gvars, l_min_age, l_max_age, grainset)
    return gvars


def plot_hist(request, gvars, min_age, max_age):
    bin_sequence = []
    age = min_age
    bin_width = float(gvars['form_values']['entHistBinwidth'])
    while age < max_age:
        bin_sequence.append(age)
        age += bin_width

    if gvars['g_prob_graph_to_draw'] == [] or gvars['g_prob_graph_to_draw'] is None:
        return

    df = pd.DataFrame(gvars['g_prob_graph_to_draw'])

    p_hist_cum = df.plot_bokeh(
        kind="hist",
        figsize=(250, 250),
        sizing_mode="scale_width",
        bins=bin_sequence,
        cumulative=True,
        vertical_xlabel=False,
        show_figure=False,
        title=gvars['g_cum_title'],
        xlabel='Age (Ma)',
        ylabel='',
        xticks=np.arange(0, max_age, 1000),
        legend=None
    )

    p_hist = df.plot_bokeh(
        kind="hist",
        figsize=(250, 250),
        sizing_mode="scale_width",
        bins=bin_sequence,
        cumulative=False,
        vertical_xlabel=False,
        show_figure=False,
        title=gvars['g_prob_title'],
        xlabel='Age (Ma)',
        ylabel='',
        xticks=np.arange(0, max_age, 1000),
        legend=None

    )

    gvars['graph_values']['ax_prob'] = p_hist
    gvars['graph_values']['ax_cum'] = p_hist_cum

    return gvars


def prob_cum_hist_plot(request, gvars, do_hist, min_age, max_age, grainset):
    if not do_hist:
        gvars = prob_cum_plot(request, gvars, min_age, max_age, grainset)
    else:
        gvars = plot_hist(request, gvars, min_age, max_age)

    return gvars


def clear_and_plot(request, gvars, grainset, *args):
    gvars['g_grainset'] = grainset
    gvars['g_filters'].sample_name_filter = []

    if gvars['varMinAgeCrop'] == 1:
        gvars['g_filters'].minAgeCrop = 0

    if gvars['varMaxAgeCrop'] == 1:
        gvars['g_filters'].maxAgeCrop = const.EarthAge

    items = gvars['form_values']['lboxSamples']
    gvars['g_filters'].sample_name_filter = items

    gui_support.fill_data_table(gvars, gvars['g_table'], grainset, gvars['pars_onChange'][0], gvars['g_list_col_names'])

    write_gvars(request, gvars)

    if gvars['g_number_of_good_grains'][0] == 0:
        return False

    do_hist = (int(gvars['g_graph_settings'].pdp_kde_hist) == 2)

    if int(gvars['g_graph_settings'].pdp_kde_hist) == 0:

        gvars['g_kde'] = grainset.kde(gvars['g_graph_settings'].bandwidth)

        if gvars['g_kde'] == [] or gvars['g_kde'] is None:
            return False

        gvars['g_ckde'] = gvars['g_kde'][2]

    elif int(gvars['g_graph_settings'].pdp_kde_hist) == 1:

        gvars['g_pdp'] = grainset.pdp(gvars['varUncType'])

        if gvars['g_pdp'] == [] or gvars['g_pdp'] is None:
            return False

        gvars['g_cpdp'] = gvars['g_pdp'][2]

    set_pval_dval(gvars)

    age_lim = min_max_ages(request, gvars, grainset)
    if int(gvars['varMinAgeCrop']) == 1:
        min_age = int(gvars['form_values']['entAgeMinCrop'])
        min_conc_x = calc_ratio(float(gvars['form_values']['entAgeMinCrop']))[1]
        min_conc_y = calc_ratio(float(gvars['form_values']['entAgeMinCrop']))[0]
    else:
        min_age = age_lim[0]
        min_conc_x = age_lim[2]
        min_conc_y = age_lim[4]
    if int(gvars['varMaxAgeCrop']) == 1:
        max_age = int(gvars['form_values']['entAgeMaxCrop'])
        max_conc_x = calc_ratio(float(gvars['form_values']['entAgeMaxCrop']))[1]
        max_conc_y = calc_ratio(float(gvars['form_values']['entAgeMaxCrop']))[0]
    else:
        max_age = age_lim[1]
        max_conc_x = age_lim[3]
        max_conc_y = age_lim[5]

    if min_age < 0:
        min_age = 2
    elif min_age == 0:
        min_age += 2
    elif (min_age > 0) and (min_age % 2 != 0):
        min_age += 1

    clear_prev_or_remove_text(request, gvars)

    conctype = concordia_type(gvars)
    conc_graph_x = conctype[0]
    conc_graph_y = conctype[1]
    conc_title = conctype[2]
    conc_graph_xtitle = conctype[3]
    conc_graph_ytitle = conctype[4]
    xconc = conctype[5]
    yconc = conctype[6]

    l_kde_pdp_hist = kde_pdp_hist(gvars, grainset)

    set_plot_types_and_titles(request, gvars, l_kde_pdp_hist)

    set_axes(request, gvars, conc_title, conc_graph_xtitle, conc_graph_ytitle, conc_graph_x, conc_graph_y,
             min_age, max_age,
             min_conc_x, max_conc_x, min_conc_y, max_conc_y)

    draw_concordia_ticks(request, gvars, xconc, yconc, min_age, max_age, min_conc_x, max_conc_x, min_conc_y, max_conc_y,
                         conc_title, conc_graph_xtitle, conc_graph_ytitle)

    if int(gvars['g_graph_settings'].pdp_kde_hist) != 2:
        plot_conc_text_peaks(request, gvars, min_age, max_age)

    plot_conc_ellipses(request, gvars, grainset)

    prob_cum_hist_plot(request, gvars, do_hist, min_age, max_age, grainset)

    return True


def create_graph_data(request):
    ax_conc = figure(
        output_backend="webgl",
        title="Concordia",
        x_axis_label='207Pb/235U',
        y_axis_label='206Pb/238U',
        sizing_mode="scale_width",
        toolbar_location='right',
        toolbar_sticky=False,
        active_drag='pan',
        x_range=Range1d(),
        y_range=Range1d()

    )

    ax_prob = figure(
        title="KDE/PDP/Histogram",
        x_axis_label='Age (ma)',
        y_axis_label='',
        sizing_mode="scale_width",
        toolbar_location='right',
        active_drag='pan',
        x_range=Range1d(0, EarthAge),
        y_range=Range1d()

    )

    ax_cum = figure(

        title="Cumulative diagrams",
        x_axis_label='Age (ma)',
        y_axis_label='',
        sizing_mode="scale_width",
        toolbar_location='right',
        active_drag='pan',
        x_range=Range1d(0, EarthAge),
        y_range=Range1d()

    )

    return {'ax_conc': ax_conc, 'ax_conc_list': [], 'ax_prob': ax_prob, 'ax_prob_list': [], 'ax_cum': ax_cum, 'ax_cum_list': []}


def init_gvars(request):
    p_gvars = const.gvars_const
    p_gvars['varUConc'] = 1000
    p_gvars['varConcType'] = 0
    p_gvars['varErrFilter'] = 5
    p_gvars['varPosDiscFilter'] = 20
    p_gvars['varNegDiscFilter'] = 10
    p_gvars['varDiscLinked2Age'] = 1
    p_gvars['varKeepPrev'] = 0
    p_gvars['varShowCalc'] = 0
    p_gvars['varLimitAgeSpectrum'] = 0
    p_gvars['varUncType'] = 1
    p_gvars['varMinAgeCrop'] = 0
    p_gvars['varMaxAgeCrop'] = 1
    p_gvars['varAgeCutoff'] = 1000
    p_gvars['varDiscCutoff'] = 1000
    p_gvars['varKDEBandwidth'] = 50
    p_gvars['varHistBinwidth'] = 50
    p_gvars['varAgeAndersen'] = 0
    p_gvars['varDiscPerc'] = 0
    p_gvars['varInclude204Ellipses'] = 0
    p_gvars['varIncludeBadEllipses'] = 0
    p_gvars['varShowErrorBars'] = 0
    p_gvars['varIncludeUncorrEllipses'] = 1
    p_gvars['g_pdp'] = []
    p_gvars['g_cpdp'] = []
    p_gvars['g_kde'] = []
    p_gvars['g_ckde'] = []
    p_gvars['g_pval_dval'] = [-1, -1]
    p_gvars['g_prev_cum'] = []
    p_gvars['g_prev_prob'] = []
    p_gvars['g_directory'] = "\Examples"
    p_gvars['g_list_col_names'] = [col.replace(" ", "") for col in const.list_col_names]
    p_gvars['g_filters'] = Filters()
    p_gvars['g_graph_settings'] = GraphSettings()
    p_gvars['g_prev_n'] = 0
    p_gvars['g_grainset'] = []
    p_gvars['form_values'] = {}
    p_gvars['pars_onChange'] = []
    p_gvars['g_table'] = []
    p_gvars['samples'] = []

    return p_gvars


def index(request, id_sample=None):
    if request.method == 'POST' and request.is_ajax():
        if 'gvars' in request.session:
            gvars = read_gvars(request)

        form = SettingsForm(request.POST, gvars['form_values'])
        resp = {}

        if form.is_valid():

            gvars['form_values']['uncType'] = form.cleaned_data['uncType']
            gvars['form_values']['lboxSamples'] = form.cleaned_data['lboxSamples']
            gvars['form_values']['cbWhichAge'] = form.cleaned_data['cbWhichAge']
            gvars['form_values']['entAgeCutoff'] = form.cleaned_data['entAgeCutoff']
            gvars['form_values']['cbPbc'] = form.cleaned_data['cbPbc']
            gvars['form_values']['entAgeAndersen'] = form.cleaned_data['entAgeAndersen']
            gvars['form_values']['cbWhichConc'] = form.cleaned_data['cbWhichConc']
            gvars['form_values']['entDiscAgeFixedLim'] = form.cleaned_data['entDiscAgeFixedLim']
            gvars['form_values']['rbDiscPerc'] = form.cleaned_data['rbDiscPerc']
            gvars['form_values']['entNegDiscFilt'] = form.cleaned_data['entNegDiscFilt']
            gvars['form_values']['entPosDiscFilt'] = form.cleaned_data['entPosDiscFilt']
            gvars['form_values']['cbDiscIntersect'] = form.cleaned_data['cbDiscIntersect']
            gvars['form_values']['cbErrFilter'] = form.cleaned_data['cbErrFilter']
            gvars['form_values']['entErrFilter'] = form.cleaned_data['entErrFilter']
            gvars['form_values']['cbUConc'] = form.cleaned_data['cbUConc']
            gvars['form_values']['entUconcCutoff'] = form.cleaned_data['entUconcCutoff']
            gvars['form_values']['chbInclude207235Err'] = bool(form.cleaned_data['chbInclude207235Err'])
            gvars['form_values']['cbConcType'] = form.cleaned_data['cbConcType']
            gvars['form_values']['cbEllipsesAt'] = form.cleaned_data['cbEllipsesAt']
            gvars['form_values']['cbShowUncorrCorrBothEllipses'] = form.cleaned_data['cbShowUncorrCorrBothEllipses']
            gvars['form_values']['chbIncludeBadEllipses'] = form.cleaned_data['chbIncludeBadEllipses']
            gvars['form_values']['cbDensityPlotType'] = form.cleaned_data['cbDensityPlotType']
            gvars['form_values']['entKDEBandwidth'] = form.cleaned_data['entKDEBandwidth']
            gvars['form_values']['entHistBinwidth'] = form.cleaned_data['entHistBinwidth']
            gvars['form_values']['chbMinAgeCrop'] = form.cleaned_data['chbMinAgeCrop']
            gvars['form_values']['entAgeMinCrop'] = form.cleaned_data['entAgeMinCrop']
            gvars['form_values']['chbMaxAgeCrop'] = form.cleaned_data['chbMaxAgeCrop']
            gvars['form_values']['entAgeMaxCrop'] = form.cleaned_data['entAgeMaxCrop']
            gvars['form_values']['chbShowCalc'] = form.cleaned_data['chbShowCalc']
            gvars['form_values']['chbKeepPrev'] = form.cleaned_data['chbKeepPrev']
            gvars['form_values']['chbLimitAgeSpectrum'] = form.cleaned_data['chbLimitAgeSpectrum']
            gvars['form_values']['chbShowErrorBars'] = form.cleaned_data['chbShowErrorBars']
            gvars['form_values']['chbShowEllipses'] = form.cleaned_data['chbShowEllipses']

            form_data = request.POST.get('form_data')
            number_in_list = int(request.POST.get('number_in_list'))
            form_field = request.POST.get('form_field')
            type_event = request.POST.get('type_event')

            if form_data:
                form_data_list = json.loads(form_data)
                lb_sample_array = []
                for field in form_data_list:
                    if field["name"] == 'lboxSamples':
                        lb_sample_array.append(field["value"])
                        gvars['form_values']['lboxSamples'] = lb_sample_array
                    else:
                        gvars['form_values'][field["name"]] = field["value"]

            items = gvars['form_values']['lboxSamples']

            gvars['g_filters'].sample_name_filter = items

            if number_in_list is not None:
                if type_event == 'ajax_save':
                    write_gvars(request, gvars)

                    fill_data_table(gvars, gvars['pars_onChange'][1], gvars['pars_onChange'][2],
                                    gvars['pars_onChange'][0], gvars['pars_onChange'][3])
                elif type_event == 'on_load':
                    form = SettingsForm()
                    write_gvars(request, gvars)
                elif type_event == 'onChange':
                    gui_support.onChange(gvars, int(number_in_list),
                                         gvars['form_values'][form_field],
                                         gvars['pars_onChange'])

                elif type_event == 'onGraphChange':
                    if form_field == 'cbConcType':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  gvars['form_values'][form_field])

                    elif form_field == 'cbEllipsesAt':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  int(gvars['form_values'][form_field]) + 1)

                    elif form_field == 'entKDEBandwidth':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  float(gvars['form_values'][form_field]))

                    elif form_field == 'entHistBinwidth':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  float(gvars['form_values'][form_field]))

                    elif form_field == 'cbDensityPlotType':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  gvars['form_values'][form_field],
                                                  gvars['form_values']['entKDEBandwidth'],
                                                  gvars['form_values']['entHistBinwidth'])

                    elif form_field == 'chbKeepPrev':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  gvars['form_values']['chbKeepPrev'],
                                                  gvars['form_values']['chbLimitAgeSpectrum'])

                    elif form_field == 'chbLimitAgeSpectrum':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  gvars['form_values']['chbLimitAgeSpectrum'],
                                                  gvars['form_values']['chbKeepPrev'])

                    elif form_field == 'chbIncludeBadEllipses':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  gvars['form_values']['chbIncludeBadEllipses'])

                    elif form_field == 'chbShowCalc':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  gvars['form_values']['chbShowCalc'],
                                                  )
                    elif form_field == 'chbShowErrorBars':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  gvars['form_values']['chbShowErrorBars'],
                                                  )
                    elif form_field == 'chbShowEllipses':
                        gui_support.onGraphChange(request, gvars, number_in_list,
                                                  gvars['form_values']['chbShowEllipses'],
                                                  )

            listcolnames = gvars['pars_onChange'][3].copy()
            listcolnames.insert(0, "Analysis name")

            # print('g_grainset', gvars['g_grainset'])

            prev_data_av = gvars['g_grainset'] != []

            resp['success'] = True
            resp['dc_table'] = gvars['pars_onChange'][1]
            resp['prev_data_av'] = prev_data_av

        else:
            resp['success'] = False
            csrf_context = {}
            csrf_context.update(csrf(request))
            form_html = render_crispy_form(form, context=csrf_context)
            resp['html'] = form_html

        write_gvars(request, gvars)

        response = JsonResponse({'resp': resp})

        return response

    else:

        data_table = []

        prev_data_av = False
        gvars = {}
        if 'gvars' in request.session:
            gvars = read_gvars(request)
            form = set_ui_elements(gvars)
        else:
            form = SettingsForm()
            gvars = init_gvars(request)
            gvars = gui_support.set_Tk_var(gvars)

        uploaded_file = gvars['uploaded_file']
        status_text = gvars['status'][0]
        status_alert = gvars['status'][1]

        form.fields['lboxSamples'].choices = gvars['samples']

        grainset = gvars['g_grainset']
        prev_data_av = grainset != []
        # gvars['g_grainset'] = pickle.dumps(grainset).hex()
        gvars['g_grainset'] = grainset

        if gvars['pars_onChange']:
            data_table = gvars['pars_onChange'][1]

        listcolnames = gvars['g_list_col_names'].copy()
        listcolnames.insert(0, "Analysis name")

        graph_values = create_graph_data(request)

        doc_ax_conc = graph_values['ax_conc']

        doc_ax_prob = graph_values['ax_prob']

        doc_ax_cum = graph_values['ax_cum']

        write_gvars(request, gvars)

        list_dict_col_names = [{"data": col} for col in listcolnames]

        script_ax_conc, div_ax_conc = components(doc_ax_conc, CDN)
        script_ax_prob, div_ax_prob = components(doc_ax_prob, CDN)
        script_ax_cum, div_ax_cum = components(doc_ax_cum, CDN)

        response = render(
            request,
            "main/index.html",
            {
                "form": form,
                'dc_table': data_table,
                'list_col_names': list_dict_col_names,
                'prev_data_av': prev_data_av,
                'uploaded_file': uploaded_file,
                'status_text': status_text,
                'status_alert': status_alert,
                'col_names': listcolnames,
                'the_script_ax_conc': script_ax_conc,
                'the_div_ax_conc': div_ax_conc,
                'the_script_ax_prob': script_ax_prob,
                'the_div_ax_prob': div_ax_prob,
                'the_script_ax_cum': script_ax_cum,
                'the_div_ax_cum': div_ax_cum,
            }
        )

        return response


def bokeh(request):
    if request.method == 'POST':
        gvars = read_gvars(request)

        grainset = gvars['pars_onChange'][2]

        gvars['graph_values'] = create_graph_data(request)

        fig_ax_conc = gvars['graph_values']['ax_conc']
        fig_ax_prob = gvars['graph_values']['ax_prob']
        fig_ax_cum = gvars['graph_values']['ax_cum']

        if gvars['form_values'] and gvars['graph_values'] and grainset:

            success = clear_and_plot(request, gvars, grainset)

            if success:

                list_renderers = []
                for rend in fig_ax_conc.renderers:
                    list_renderers.append(rend)

                plot_ellipses = int(gvars['varShowEllipses'])
                if plot_ellipses == 1:
                    dict_ellipses = {idx: val for idx, val in enumerate(gvars['graph_values']['ax_conc_list'])}
                    ellipses = hv.NdOverlay(dict_ellipses)  # ellipses
                    fig_ax_conc_ellipses = hv.render(ellipses, backend='bokeh')

                    for rend in fig_ax_conc_ellipses.renderers:
                        list_renderers.append(rend)

                fig_ax_conc.renderers = list_renderers
                fig_ax_conc.output_backend = "webgl"

                do_hist = (int(gvars['g_graph_settings'].pdp_kde_hist) == 2)

                if not do_hist:

                    layout_ax_prob = hv.Overlay(gvars['graph_values']['ax_prob_list'])
                    layout_ax_prob.opts(
                        responsive=True,
                        show_grid=True,
                        title=gvars['g_prob_title'],
                        xlabel='Age (Ma)',
                        yaxis=None,
                        tools=['pan', 'box_zoom', 'wheel_zoom', 'undo', 'redo', 'reset', 'save'],
                        aspect='square'
                    )
                    fig_ax_prob = hv.render(layout_ax_prob, backend='bokeh')

                    layout_ax_cum = hv.Overlay(gvars['graph_values']['ax_cum_list'])
                    layout_ax_cum.opts(
                        responsive=True,
                        show_grid=True,
                        title=gvars['g_cum_title'],
                        xlabel='Age (Ma)',
                        yaxis=None,
                        tools=['pan', 'box_zoom', 'wheel_zoom', 'undo', 'redo', 'reset', 'save'],
                        aspect='square'
                    )
                    fig_ax_cum = hv.render(layout_ax_cum, backend='bokeh')

                else:
                    fig_ax_prob = gvars['graph_values']['ax_prob']
                    fig_ax_cum = gvars['graph_values']['ax_cum']

            script_ax_conc, div_ax_conc = components(fig_ax_conc, CDN)
            script_ax_prob, div_ax_prob = components(fig_ax_prob, CDN)
            script_ax_cum, div_ax_cum = components(fig_ax_cum, CDN)

            response = JsonResponse(
                {
                    'script_ax_conc': script_ax_conc,
                    'div_ax_conc': div_ax_conc,
                    'script_ax_prob': script_ax_prob,
                    'div_ax_prob': div_ax_prob,
                    'script_ax_cum': script_ax_cum,
                    'div_ax_cum': div_ax_cum,
                    # 'g_grainset': pickle.dumps(grainset).hex(),
                    'success': success
                }
            )

            gvars['graph_values'] = {}
            write_gvars(request, gvars)

            return response


def statistics(request):
    if request.method == 'POST':

        gvars = None
        if 'gvars' in request.session:
            gvars = read_gvars(request)

        grainset = gvars['pars_onChange'][2]

        elements = ["number of good grains", "weighted average age", "±1σ", "95% conf.", "MSWD", "max age", "min age"]
        dict_of_labels = {}
        counter = 0
        for n in elements:
            dict_of_labels[n] = round(gvars['g_number_of_good_grains'][counter], 2)
            counter += 1

        if gvars['g_number_of_good_grains'][0] != 0:
            dict_of_labels["peaks: weight"] = calc_peaks_weight(peaks(gvars), grainset)
            dict_of_labels["KS p-val"] = round(gvars['g_pval_dval'][0], 2)
            dict_of_labels["KS d-val"] = round(gvars['g_pval_dval'][1], 2)
            dict_of_labels["Likeness"] = round(gvars['g_pval_dval'][2], 2)
            dict_of_labels["Similarity"] = round(gvars['g_pval_dval'][3], 2)
        else:
            dict_of_labels["peaks: weight"] = ""
            dict_of_labels["KS p-val"] = ""
            dict_of_labels["KS d-val"] = ""
            dict_of_labels["Likeness"] = ""
            dict_of_labels["Similarity"] = ""

        html_data = "<table border='0' width='100%'>"
        for k, v in dict_of_labels.items():
            html_data += "<tr>"
            html_data += "<td>" + str(k) + ": </td><td>" + str(v) + "</td>"
            html_data += "</tr>"
        html_data += "</table>"
        return HttpResponse(json.dumps(html_data))
