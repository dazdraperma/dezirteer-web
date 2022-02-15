import pickle
import logging
import time
from functools import partial
from math import *
from multiprocessing import Pool

from django.contrib import messages

import sys
import ctypes

from .const import *
from .math_module import *

logger = logging.getLogger('support_log')

global g_corr_type
g_corr_type = ["none", "204", "207", "208", "And."]


class NoGrainsError(Exception):
    pass


class GraphSettings(object):
    def __init__(self, show_multiple=False, conc_type=0, ellipses_at=1, fit_disc=False,
                 anchored=False, pdp_kde_hist=0, do_hist=False, bandwidth=50, binwidth=50, keep_previous=False):
        self.__show_multiple = show_multiple
        self.__conc_type = conc_type
        self.__ellipses_at = ellipses_at
        self.__fit_disc = fit_disc
        self.__anchored = anchored
        self.__pdp_kde_hist = pdp_kde_hist
        self.__do_hist = do_hist
        self.__bandwidth = bandwidth
        self.__binwidth = binwidth
        self.__keep_previous = keep_previous

    @property
    def show_multiple(self):
        return self.__show_multiple

    @show_multiple.setter
    def show_multiple(self, value):
        self.__show_multiple = value

    @property
    def conc_type(self):
        return self.__conc_type

    @conc_type.setter
    def conc_type(self, value):
        self.__conc_type = value

    @property
    def ellipses_at(self):
        return self.__ellipses_at

    @ellipses_at.setter
    def ellipses_at(self, value):
        self.__ellipses_at = value

    @property
    def fit_disc(self):
        return self.__fit_disc

    @fit_disc.setter
    def fit_disc(self, value):
        self.__fit_disc = value

    @property
    def anchored(self):
        return self.__anchored

    @anchored.setter
    def anchored(self, value):
        self.__anchored = value

    @property
    def pdp_kde_hist(self):
        return self.__pdp_kde_hist

    @pdp_kde_hist.setter
    def pdp_kde_hist(self, value):
        self.__pdp_kde_hist = value

    @property
    def do_hist(self):
        return self.__do_hist

    @do_hist.setter
    def do_hist(self, value):
        self.__do_hist = value

    @property
    def bandwidth(self):
        return self.__bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        self.__bandwidth = value

    @property
    def binwidth(self):
        return self.__binwidth

    @binwidth.setter
    def binwidth(self, value):
        self.__binwidth = value

    @property
    def keep_previous(self):
        return self.__keep_previous

    @keep_previous.setter
    def keep_previous(self, value):
        self.__keep_previous = value


# def write_var(request, key, val):
#     request.session[key] = pickle.dumps(val, pickle.HIGHEST_PROTOCOL).hex()


def read_var(request, key):
    return pickle.loads(bytes.fromhex(request.session[key]))


def set_vars(gvars, form_numbers):
    gvars['varUConc'] = 1000
    gvars['varDiscType'] = 0
    gvars['varConcType'] = 0
    gvars['varEllipseSigma'] = 0
    gvars['varAgebased'] = 0
    gvars['varUncorrOrPbc'] = 0
    gvars['varErrFilter'] = 0
    gvars['varShowMultiple'] = 0
    gvars['varDrawKde'] = 0
    gvars['varPosDiscFilter'] = 20
    gvars['varNegDiscFilter'] = 10
    gvars['varFitDiscordia'] = 0
    gvars['varDrawPDP'] = 0
    gvars['varDrawKDE'] = 0
    gvars['varDrawCPDP'] = 0
    gvars['varDrawCKDE'] = 0
    gvars['varDrawHist'] = 0
    gvars['var_pdp_kde_hist'] = 0
    gvars['varAnchored'] = 0
    gvars['varDiscLinked2Age'] = 1
    gvars['varKeepPrev'] = 0
    gvars['varTypePbc'] = 0
    gvars['varShowCalc'] = 0
    gvars['varInclude207235Err'] = 0
    gvars['varLimitAgeSpectrum'] = 0
    gvars['varUncType'] = 1
    gvars['varCommPb'] = 0
    gvars['varMinAgeCrop'] = 0
    gvars['varMaxAgeCrop'] = 4600
    gvars['varAgeCutoff'] = 1000
    gvars['varDiscCutoff'] = 100
    gvars['varKDEBandwidth'] = 50
    gvars['varHistBinwidth'] = 50
    gvars['varAgeAndersen'] = 0
    gvars['varDiscPerc'] = 0
    gvars['varInclude204Ellipses'] = 0
    gvars['varIncludeBadEllipses'] = 1
    gvars['varIncludeUncorrEllipses'] = 1
    gvars['varShowErrorBars'] = 0

    pars = gvars['pars_onChange']
    for key, value in gvars['form_values'].items():
        if not value:
            continue
        if form_numbers[key] == 1:
            pars[0].show_multiple = int(value)
        elif form_numbers[key] == 2:
            pars[0].filter_by_uconc[0] = True if int(value) == 1 else False
        elif form_numbers[key] == 3:
            pars[0].which_age[0] = 1 if value == '' else int(value)
        elif form_numbers[key] == 4:
            pars[0].use_pbc = [int(value), gvars['varAgeAndersen']]
        elif form_numbers[key] == 5:
            pars[0].filter_by_err[0] = int(value)
        elif form_numbers[key] == 6:
            pars[0].pos_disc_filter = int(value) / 100
        elif form_numbers[key] == 7:
            pars[0].neg_disc_filter = int(value) / 100 * (-1)
        elif form_numbers[key] == 8:
            pars[0].disc_type[0] = int(value)
        elif form_numbers[key] == 9:
            pars[0].conc_type = int(value)
        elif form_numbers[key] == 11:
            pars[0].fit_disc = int(value)
        elif form_numbers[key] == 12:
            pars[0].anchored = int(value)
        elif form_numbers[key] == 13:
            if (type(value) is str) and (str(value) == 'on'):
                value = 1
            else:
                value = 0
            pars[0].do_pdp = int(value)
        elif form_numbers[key] == 14:
            pars[0].do_kde = int(value)
        elif form_numbers[key] == 15:
            pars[0].do_cpdp = int(value)
        elif form_numbers[key] == 16:
            pars[0].do_ckde = int(value)
        elif form_numbers[key] == 17:
            pars[0].do_hist = int(value)
        elif form_numbers[key] == 18:
            pars[0].filter_by_uconc[1] = int(value)
        elif form_numbers[key] == 19:
            pars[0].which_age[1] = int(value)
        elif form_numbers[key] == 20:
            pars[0].filter_by_err[1] = int(value) / 100
        elif form_numbers[key] == 21:
            pass
        elif form_numbers[key] == 22:
            if (type(value) is str) and (str(value) == 'on'):
                value = 1
            else:
                value = 0
            pars[0].include207235Err = int(value)
        elif form_numbers[key] == 23:
            pars[0].unc_type = '1' if value == '' else value
        elif form_numbers[key] == 24:
            pars[0].filter_by_commPb = int(value)
        elif form_numbers[key] == 25:
            pars[0].disc_type[1] = int(value)
        elif form_numbers[key] == 28:
            pars[0].andersenAge = int(value)
        elif form_numbers[key] == 29:
            pars[0].discOrIntersect = int(value)
        elif form_numbers[key] == 30:
            pars[0].intersectAt = int(value) + 1
        elif form_numbers[key] == 31:
            pars[0].speed_or_pbc == int(value)

    gvars['pars_onChange'] = pars
    gvars['g_filters'] = pars[0]
    return gvars


def onChange(gvars, p_number_in_list, p_value, pars, *args, **kwargs):
    if p_number_in_list == 1:
        pars[0].show_multiple = int(p_value)
    elif p_number_in_list == 2:
        pars[0].filter_by_uconc[0] = True if int(p_value) == 1 else False
    elif p_number_in_list == 3:
        pars[0].which_age[0] = int(p_value)
    elif p_number_in_list == 4:
        pars[0].use_pbc = [int(p_value), int(gvars['varAgeAndersen'])]
    elif p_number_in_list == 5:
        pars[0].filter_by_err[0] = int(p_value)
    elif p_number_in_list == 6:
        pars[0].pos_disc_filter = int(p_value) / 100
    elif p_number_in_list == 7:
        pars[0].neg_disc_filter = int(p_value) / 100 * (-1)
    elif p_number_in_list == 8:
        pars[0].disc_type[0] = int(p_value)
    elif p_number_in_list == 9:
        pars[0].conc_type = int(p_value)
    elif p_number_in_list == 11:
        pars[0].fit_disc = int(p_value)
    elif p_number_in_list == 12:
        pars[0].anchored = int(p_value)
    elif p_number_in_list == 13:
        if (type(p_value) is str) and (str(p_value) == 'on'):
            value = 1
        else:
            value = 0
        pars[0].do_pdp = int(value)
    elif p_number_in_list == 14:
        pars[0].do_kde = int(p_value)
    elif p_number_in_list == 15:
        pars[0].do_cpdp = int(p_value)
    elif p_number_in_list == 16:
        pars[0].do_ckde = int(p_value)
    elif p_number_in_list == 17:
        pars[0].do_hist = int(p_value)
    elif p_number_in_list == 18:
        pars[0].filter_by_uconc[1] = int(p_value)
    elif p_number_in_list == 19:
        pars[0].which_age[1] = int(p_value)
    elif p_number_in_list == 20:
        pars[0].filter_by_err[1] = int(p_value) / 100
    elif p_number_in_list == 21:
        pass
    elif p_number_in_list == 22:
        if (type(p_value) is str) and (str(p_value) == 'on'):
            value = 1
        else:
            value = 0
        gvars['varInclude207235Err'] = value
        pars[0].include207235Err = value
    elif p_number_in_list == 23:
        gvars['varUncType'] = int(p_value)
        pars[0].unc_type = int(p_value)
    elif p_number_in_list == 24:
        pars[0].filter_by_commPb = int(p_value)
    elif p_number_in_list == 25:
        pars[0].disc_type[1] = int(p_value)
    elif p_number_in_list == 26:
        if (type(p_value) is str) and (str(p_value) == 'on'):
            value = 1
        else:
            value = 0
        gvars['varMinAgeCrop'] = value
    elif p_number_in_list == 261:
        if int(gvars['varMinAgeCrop']) == 0:
            pars[0].minAgeCrop = 0
        else:
            try:
                pars[0].minAgeCrop = float(p_value)
            except ValueError:
                pars[0].minAgeCrop = 0
    elif p_number_in_list == 27:
        if (type(p_value) is str) and (str(p_value) == 'on'):
            value = 1
        else:
            value = 0
        gvars['varMaxAgeCrop'] = value
        pars[0].maxAgeCrop = EarthAge
    elif p_number_in_list == 271:
        if int(gvars['varMaxAgeCrop']) == 0:
            pars[0].maxAgeCrop = EarthAge
        else:
            try:
                pars[0].maxAgeCrop = float(p_value)
            except ValueError:
                pars[0].maxAgeCrop = 0
    elif p_number_in_list == 28:
        pars[0].andersenAge = int(p_value)
        gvars['varAgeAndersen'] = int(p_value)
    elif p_number_in_list == 29:
        pars[0].discOrIntersect = int(p_value)
        gvars['varDiscPerc'] = int(p_value)
    elif p_number_in_list == 30:
        if p_value == '':
            p_value = '0'
            pars[0].intersectAt = int(p_value) + 1
    elif p_number_in_list == 31:
        pars[0].speed_or_pbc == int(p_value)

    res = fill_data_table(gvars, pars[1], pars[2], pars[0], pars[3])
    gvars['pars_onChange'] = pars
    gvars['g_filters'] = pars[0]

    return gvars


def onGraphChange(request, gvars, p_number_in_list, p_value, *args, **kwargs):
    if p_number_in_list == 0:
        gvars['g_graph_settings'].conc_type = int(p_value)
    elif p_number_in_list == 1:
        gvars['g_graph_settings'].conc_type = int(p_value)
    elif p_number_in_list == 2:
        gvars['g_graph_settings'].ellipses_at = int(p_value)
    elif p_number_in_list == 7:
        gvars['g_graph_settings'].pdp_kde_hist = int(p_value)
        if p_value == 0:
            # write_var(request, 'varShowCalc', 0)
            gvars['varShowCalc'] = 0
    elif p_number_in_list == 11:
        gvars['g_graph_settings'].bandwidth = int(p_value)
    elif p_number_in_list == 12:
        gvars['g_graph_settings'].binwidth = int(p_value)
    elif p_number_in_list == 13:

        if (type(p_value) is str) and (str(p_value) == 'on'):

            value = 1
            gvars['varLimitAgeSpectrum'] = 0
        else:
            value = 0
        # write_var(request, 'varKeepPrev', value)
        gvars['varKeepPrev'] = value
    elif p_number_in_list == 131:

        if (type(p_value) is str) and (str(p_value) == 'on'):
            value = 1
            # write_var(request, 'varKeepPrev', 0)
            gvars['varKeepPrev'] = 0
        else:
            value = 0
        # write_var(request, 'varLAS', value)
        gvars['varLimitAgeSpectrum'] = value

    elif p_number_in_list == 32:
        if (type(p_value) is str) and (str(p_value) == 'on'):
            value = 1
        else:
            value = 0
        gvars['varIncludeBadEllipses'] = value
    elif p_number_in_list == 33:
        if (type(p_value) is str) and (str(p_value) == 'on'):
            value = 1
        else:
            value = 0
        gvars['varShowCalc'] = value
    elif p_number_in_list == 34:
        if (type(p_value) is str) and (str(p_value) == 'on'):
            value = 1
        else:
            value = 0
        gvars['varShowErrorBars'] = value
    elif p_number_in_list == 35:
        if (type(p_value) is str) and (str(p_value) == 'on'):
            value = 1
        else:
            value = 0
            gvars['varShowErrorBars'] = 1
            gvars['varIncludeBadEllipses'] = 0
        gvars['varShowEllipses'] = value

    fill_data_table(gvars, gvars['pars_onChange'][1], gvars['pars_onChange'][2], gvars['pars_onChange'][0],
                    gvars['pars_onChange'][3])
    return gvars


def set_Tk_var(gvars):
    gvars['varUConc'] = 1000
    gvars['varConcType'] = 0
    gvars['varErrFilter'] = 5
    gvars['varPosDiscFilter'] = 20
    gvars['varNegDiscFilter'] = 10
    gvars['varDiscLinked2Age'] = 1
    gvars['varKeepPrev'] = 0
    gvars['varShowCalc'] = 0
    gvars['varInclude207235Err'] = 0
    gvars['varLimitAgeSpectrum'] = 0
    gvars['varUncType'] = 1
    gvars['varMinAgeCrop'] = 0
    gvars['varMaxAgeCrop'] = 1000
    gvars['varAgeCutoff'] = 1000
    gvars['varDiscCutoff'] = 1000
    gvars['varKDEBandwidth'] = 50
    gvars['varHistBinwidth'] = 50
    gvars['varAgeAndersen'] = 0
    gvars['varDiscPerc'] = 0
    gvars['varInclude204Ellipses'] = 0
    gvars['varIncludeBadEllipses'] = 0
    gvars['varIncludeUncorrEllipses'] = 1
    gvars['varShowErrorBars'] = 0
    return gvars


def init(pTop, pGui, *args, **kwargs):
    global w, top_level, root
    w = pGui
    top_level = pTop
    root = pTop


def destroy_window():
    global top_level
    top_level.destroy()
    top_level = None


def line_with_data(gvars, p_grainset, p_filters):
    if not p_grainset.analyses_list:
        pass
    j = 0
    unc_type = int(p_filters.unc_type)
    an_list = p_grainset.analyses_list
    good_grains = p_grainset.good_bad_sets(p_filters)
    grainset = p_grainset
    filters = p_filters
    l_type_pbc = p_filters.use_pbc[0]
    one_analysis = []
    list_of_analyses = []
    while j < len(grainset):
        one_analysis = []
        th232_u238 = an_list[j].th232_u238
        pb208_th232 = an_list[j].pb208_th232
        pb207_pb206 = an_list[j].pb207_pb206
        pb207_u235 = an_list[j].pb207_u235
        pb206_u238 = an_list[j].pb206_u238
        corr_coef_75_68 = an_list[j].corr_coef_75_68
        corr_coef_86_76 = an_list[j].corr_coef_86_76
        u_conc = an_list[j].u_conc
        pbc = an_list[j].pbc
        pb206_pb204 = an_list[j].pb206_pb204
        pb207_pb204 = an_list[j].pb207_pb204
        pb208_pb204 = an_list[j].pb208_pb204
        th232_pb204 = an_list[j].th232_pb204
        u238_pb204 = an_list[j].u238_pb204
        age_208_232 = an_list[j].age82
        age_207_206 = an_list[j].age76
        age_207_235 = an_list[j].age75
        age_206_238 = an_list[j].age68
        pbc204_age_206_238 = an_list[j].age68_204corr
        pbc204_age_207_235 = an_list[j].age75_204corr
        pbc204_age_208_232 = an_list[j].age82_204corr
        pbc204_age_207_206 = an_list[j].age76_204corr
        pbc207_age = an_list[j].age_207corr
        pbc208_age = an_list[j].age_208corr
        rat68_204corr = an_list[j].rat68_204corr
        rat75_204corr = an_list[j].rat75_204corr
        rat82_204corr = an_list[j].rat82_204corr
        rat76_204corr = an_list[j].rat76_204corr

        if p_filters.use_pbc[0] == 4:
            pbcAnd_age = an_list[j].calc_age(0, [4, gvars['varAgeAndersen']])
        else:
            pbcAnd_age = [-1, -1, -1]
        disc_76_68 = 100 * an_list[j].calc_discordance(2, p_filters.disc_type[1], p_filters.use_pbc)
        disc_75_68 = 100 * an_list[j].calc_discordance(3, p_filters.disc_type[1], p_filters.use_pbc)
        is_grain_good = an_list[j].is_grain_good(filters)
        if is_grain_good[1] == 3:
            best_age_system = "207Pb/206Pb"
        else:
            best_age_system = "206Pb/238U"
        best_age = an_list[j].calc_age(is_grain_good[1], p_filters.use_pbc)

        one_analysis.append(round(th232_u238[0], 4))
        one_analysis.append(round(th232_u238[1], 4))
        one_analysis.append(round(th232_u238[2], 4))

        one_analysis.append(round(pb208_th232[0], 4))
        one_analysis.append(round(pb208_th232[1], 4))
        one_analysis.append(round(pb208_th232[1], 4))

        one_analysis.append(round(pb207_pb206[0], 4))
        one_analysis.append(round(pb207_pb206[1], 4))
        one_analysis.append(round(pb207_pb206[2], 4))

        one_analysis.append(round(pb207_u235[0], 4))
        one_analysis.append(round(pb207_u235[1], 4))
        one_analysis.append(round(pb207_u235[2], 4))

        one_analysis.append(round(pb206_u238[0], 4))
        one_analysis.append(round(pb206_u238[1], 4))
        one_analysis.append(round(pb206_u238[2], 4))

        one_analysis.append(round(corr_coef_75_68, 2))
        one_analysis.append(round(corr_coef_86_76, 2))

        one_analysis.append(round(u_conc[0], 4))
        one_analysis.append(round(u_conc[1], 4))
        one_analysis.append(round(u_conc[2], 4))

        one_analysis.append(round(pbc[0], 4))
        one_analysis.append(round(pbc[1], 4))
        one_analysis.append(round(pbc[2], 4))

        one_analysis.append(round(pb206_pb204[0], 1))
        one_analysis.append(round(pb206_pb204[1], 1))
        one_analysis.append(round(pb206_pb204[2], 1))

        one_analysis.append(round(pb207_pb204[0], 1))
        one_analysis.append(round(pb207_pb204[1], 1))
        one_analysis.append(round(pb207_pb204[2], 1))

        one_analysis.append(round(pb208_pb204[0], 1))
        one_analysis.append(round(pb208_pb204[1], 1))
        one_analysis.append(round(pb208_pb204[2], 1))

        one_analysis.append(round(th232_pb204[0], 1))
        one_analysis.append(round(th232_pb204[1], 1))
        one_analysis.append(round(th232_pb204[2], 1))

        one_analysis.append(round(u238_pb204[0], 1))
        one_analysis.append(round(u238_pb204[1], 1))
        one_analysis.append(round(u238_pb204[2], 1))

        one_analysis.append(int(age_208_232[0]))
        one_analysis.append(int(age_208_232[1]))
        one_analysis.append(int(age_208_232[2]))

        one_analysis.append(int(age_207_206[0]))
        one_analysis.append(int(age_207_206[1]))
        one_analysis.append(int(age_207_206[2]))

        one_analysis.append(int(age_207_235[0]))
        one_analysis.append(int(age_207_235[1]))
        one_analysis.append(int(age_207_235[2]))

        one_analysis.append(int(age_206_238[0]))
        one_analysis.append(int(age_206_238[1]))
        one_analysis.append(int(age_206_238[2]))

        one_analysis.append(g_corr_type[l_type_pbc])

        one_analysis.append(round(rat68_204corr[0], 4))
        one_analysis.append(round(rat68_204corr[1], 4))
        one_analysis.append(round(rat68_204corr[2], 4))
        one_analysis.append(round(rat75_204corr[0], 4))
        one_analysis.append(round(rat75_204corr[1], 4))
        one_analysis.append(round(rat75_204corr[2], 4))
        one_analysis.append(round(rat82_204corr[0], 4))
        one_analysis.append(round(rat82_204corr[1], 4))
        one_analysis.append(round(rat82_204corr[2], 4))
        one_analysis.append(round(rat76_204corr[0], 4))
        one_analysis.append(round(rat76_204corr[1], 4))
        one_analysis.append(round(rat76_204corr[2], 4))

        one_analysis.append(int(pbc204_age_206_238[0]))
        one_analysis.append(int(pbc204_age_206_238[1]))
        one_analysis.append(int(pbc204_age_206_238[2]))
        one_analysis.append(int(pbc204_age_207_235[0]))
        one_analysis.append(int(pbc204_age_207_235[1]))
        one_analysis.append(int(pbc204_age_207_235[2]))
        one_analysis.append(int(pbc204_age_208_232[0]))
        one_analysis.append(int(pbc204_age_208_232[1]))
        one_analysis.append(int(pbc204_age_208_232[2]))
        one_analysis.append(int(pbc204_age_207_206[0]))
        one_analysis.append(int(pbc204_age_207_206[1]))
        one_analysis.append(int(pbc204_age_207_206[2]))
        one_analysis.append(int(pbc207_age[0]))
        one_analysis.append(int(pbc207_age[1]))
        one_analysis.append(int(pbc207_age[2]))
        one_analysis.append(int(pbc208_age[0]))
        one_analysis.append(int(pbc208_age[1]))
        one_analysis.append(int(pbc208_age[2]))
        one_analysis.append(int(pbcAnd_age[0]))
        one_analysis.append(int(pbcAnd_age[1]))
        one_analysis.append(int(pbcAnd_age[2]))
        one_analysis.append(str(gvars['varAgeAndersen']))
        one_analysis.append(int(disc_76_68))
        one_analysis.append(int(disc_75_68))
        one_analysis.append(str(is_grain_good[0]))
        one_analysis.append(best_age_system)

        one_analysis.append(int(best_age[0]))
        one_analysis.append(int(best_age[unc_type]))

        list_of_analyses.append(one_analysis)
        one_analysis = []
        j += 1
    return list_of_analyses


def get_tab_dict_by_threading(tab_array, col_names, an_list, idx):
    d = {col[1]: str(tab_array[idx][col[0]]) for col in enumerate(col_names)}
    d['Analysis name'] = str(an_list[idx])
    return d


def fill_data_table(gvars, p_table, p_grainset, p_filters, p_colnames, *args):
    if not p_grainset.analyses_list:
        pass

    an_list = p_grainset.analyses_list

    # good_grains = p_grainset.good_bad_sets(gvars['pars_onChange'][0])
    # table_array = line_with_data(gvars, p_grainset, gvars['pars_onChange'][0])

    gvars['g_number_of_good_grains'] = p_grainset.good_bad_sets(p_filters)
    table_array = line_with_data(gvars, p_grainset, p_filters)

    p_table.clear()

    start_1 = time.time()

    if len(p_grainset) > 100000:  # multithreading
        print('multi ', len(p_grainset))
        iterable = list(range(0, len(p_grainset)))
        pool = Pool()
        func = partial(get_tab_dict_by_threading, table_array, p_colnames, an_list)
        p_t = pool.map(func, iterable)
        pool.close()
        pool.join()
        p_table.extend(p_t)

    else:
        print('not multi ', len(p_grainset))
        j = 0
        while j < len(p_grainset):
            d = {col[1]: str(table_array[j][col[0]]) for col in enumerate(p_colnames)}

            d['Analysis name'] = str(an_list[j])
            p_table.append(d)
            j += 1

    end_1 = time.time()
    print("fill_data_table: " + str(end_1 - start_1))

