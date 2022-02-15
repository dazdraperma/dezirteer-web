LAMBDA_232 = 4.934E-11  # Amelin and Zaitsev, 2002.
# LAMBDA_232 = 4.9475E-11 #old value, used in isoplot
ERR_LAMBDA_232 = 0.015E-11  # Amelin and Zaitsev, 2002.

LAMBDA_235 = 9.8485E-10
# ERR_LAMBDA_235 =

LAMBDA_238 = 1.55125E-10
# ERR_LAMBDA_238 =

U238_U235 = 137.817  # https://doi.org/10.1016/j.gca.2018.06.014
# U238_U235 = 137.88 #old value, used in isoplot

ERR_U238_U235 = 0.031  ##https://doi.org/10.1016/j.gca.2018.06.014

lambdas = [LAMBDA_238, LAMBDA_235, LAMBDA_232]

isotope_ratios = ["U238_Pb206", "U235_Pb207", "Th232_Pb208", "Pb206_Pb207"]

minerals = ["zircon", "baddeleyite", "perovskite", "monazite", "apatite"]

EarthAge: int = 4600

sqrt2pi = 2.506628274631

listColumnNames = ['Th232/Pb208', 'err.Th232/Pb208',
                   '206Pb/207Pb', 'err.206Pb/207Pb',
                   '235U/207Pb', 'err.235U/207Pb',
                   '238U/206Pb', 'err.238U/206Pb',
                   'corr.',
                   'Age_232Th/208Pb', 'err.Age_232Th/208Pb',
                   'Age_206Pb/207Pb', 'err.Age_206Pb/207Pb',
                   'Age_238U/206Pb', 'err.Age_238U/206Pb',
                   'Age_235U/207Pb', 'err.Age_235U/207Pb',
                   '%disc.67-86', '%disc.86-57', 'is grain good?']

list_col_names = ['232Th/238U', '232/238Err1s(Int)',
                  '232/238Err 1s(Prop)',
                  '208Pb/232Th', '208/232Err1s(Int)',
                  '208/232Err1s(Prop)',
                  '207Pb/206Pb', '207/206Err1s(Int)',
                  '207/206Err1s(Prop)',
                  '207Pb/235U', '207/235Err1s(Int)',
                  '207/235Err 1s(Prop)',
                  '206Pb/238U', '206/238Err1s(Int)',
                  '206/238Err1s(Prop)',
                  'corrcoef75_68', 'corr_coef_86_76',

                  'Uconc(approx_ppm)', 'UconcErr1s(Int)',
                  'UconcErr1s(Prop)',
                  'pbc (approx_ppm)', 'pbcErr1s(Int)',
                  'pbcErr1s(Prop)',
                  '206Pb/204Pb', '206/204Err1s(Int)',
                  '206/204Err1s(Prop)',
                  '207Pb/204Pb', '207/204Err1s(Int)',
                  '207/204Err1s(Prop)',
                  '208Pb/204Pb', '208/204Err1s(Int)',
                  '208/204Err 1s(Prop)',
                  '232Th/204Pb', '232/204Err1s(Int)',
                  '232/204Err1s(Prop)',
                  '238U/204Pb', '238/204Err1s(Int)',
                  '238/204Err1s(Prop)',

                  'Age208Pb/232Th', 'Age208/232Err1s(Int)',
                  'Age208/232Err1s(Prop)',
                  'Age 207Pb/206Pb', 'Age207/206Err1s(Int)',
                  'Age207/206Err1s(Prop)',
                  'Age 207Pb/235U', 'Age207/235Err 1s(Int)',
                  'Age207/235Err 1s(Prop)',
                  'Age 206Pb/238U', 'Age206/238Err 1s(Int)',
                  'Age206/238Err 1s(Prop)',

                  'Corr_type',

                  'Pb204-corr_ 68 rat',
                  'Pb204-corr_ 68 rat Err 1s(Int)',
                  'Pb204-corr_ 68 rat Err 1s(Prop)',

                  'Pb204-corr_ 75 rat',
                  'Pb204-corr_ 75 rat Err 1s(Int)',
                  'Pb204-corr_ 75 rat Err 1s(Prop)',

                  'Pb204-corr_ 82 rat',
                  'Pb204-corr_ 82 rat Err 1s(Int)',
                  'Pb204-corr_ 82 rat Err 1s(Prop)',

                  'Pb204-corr_ 76 rat',
                  'Pb204-corr_ 76 rat Err 1s(Int)',
                  'Pb204-corr_ 76 rat Err 1s(Prop)',

                  'Pb204-corr_ 68 age',
                  'Pb204-corr_ 68 age Err 1s(Int)',
                  'Pb204-corr_ 68 age Err 1s(Prop)',

                  'Pb204-corr_ 75 age',
                  'Pb204-corr_ 75 age Err 1s(Int)',
                  'Pb204-corr_ 75 age Err 1s(Prop)',

                  'Pb204-corr_ 82 age',
                  'Pb204-corr_ 82 age Err 1s(Int)',
                  'Pb204-corr_ 82 age Err 1s(Prop)',

                  'Pb204-corr_ 76 age',
                  'Pb204-corr_ 76 age Err 1s(Int)',
                  'Pb204-corr_ 76 age Err 1s(Prop)',

                  'Pb207-corr_ age',
                  'Pb207-corr_ age Err 1s(Int)',
                  'Pb207 age corr_Err 1s(Prop)',

                  'Pb208-corr_ age',
                  'Pb208-corr_ age Err 1s(Int)',
                  'Pb208-corr_ age Err 1s(Prop)',

                  'And-corr_ age',
                  'And-corr_ age Err 1s(Int)',
                  'And-corr_ age Err 1s(Prop)',
                  'And_ intercept age',

                  'disc_ 207/206-206/238', 'disc_ 207/235-206/238',
                  'is grain good?', 'best age system',
                  'best age', 'best ageErr 1s',

                  ]

form_numbers = {'uncType': 23, 'lboxSamples': 0, 'cbWhichAge': 3, 'entAgeCutoff': 19, 'cbPbc': 4,
                'entAgeAndersen': 28, 'cbWhichConc': 8, 'entDiscAgeFixedLim': 25, 'rbDiscPerc': 29,
                'entNegDiscFilt': 7, 'entPosDiscFilt': 6, 'cbDiscIntersect': 30, 'cbErrFilter': 5,
                'entErrFilter': 20, 'cbUConc': 2, 'entUconcCutoff': 18, 'chbInclude207235Err': 22, 'cbConcType': 0,
                'cbEllipsesAt': 2, 'cbShowUncorrCorrBothEllipses': False,
                'cbDensityPlotType': 7, 'entKDEBandwidth': 11, 'entHistBinwidth': 12, 'chbMinAgeCrop': 26,
                'entAgeMinCrop': 261, 'chbMaxAgeCrop': 27, 'entAgeMaxCrop': 271,
                'chbKeepPrev': 13, 'chbLimitAgeSpectrum': 131, 'chbIncludeBadEllipses': 32, 'chbShowCalc': 33,
                'chbShowErrorBars': 34, 'chbShowEllipses': 35}

gvars_const = {
    'g_list_col_names': [col.replace(" ", "") for col in list_col_names],
    'g_grainset': None,
    'g_filters': None,
    'g_graph_settings': None,
    'prob_fig': None,
    'prob_subplot': None,
    'g_table': [],
    'dc_table': None,
    'gl_table': None,
    'g_list_of_samples': None,
    'g_directory': None,
    'g_number_of_good_grains': None,
    'g_prev_cum': None,
    'g_prev_prob': None,
    'g_prev_n': None,
    'g_kde': None,
    'g_pdp': None,
    'g_cpdp': None,
    'g_ckde': None,
    'g_pval_dval': None,
    'g_cum_graph_to_draw': None,
    'g_prob_title': None,
    'g_cum_title': None,
    'pars_onChange': None,
    'samples': None,
    'form_values': {},
    'varKeepPrev': 0,
    'varLimitAgeSpectrum': 0,
    'varMinAgeCrop': 0,
    'varUncType': 1,
    'varMaxAgeCrop': 4600,
    'g_plot_txt': None,
    'g_prob_graph_to_draw': None,
    'varIncludeBadEllipses': 0,
    'g_conc_txt_green': None,
    'g_conc_txt_blue': None,
    'g_file_type': None,
    'varAgeAndersen': 0,
    'graph_values': {},
    'pbpb_table': [],
    'concordia_table': [],
    'varInclude207235Err': 0,
    'varShowCalc': 0,
    'varDiscPerc': 0,
    'keep_prev_data': 0,
    'uploaded_file': '',
    'status': ['', 'alert-success'],
    'lbShowStatus': '',
    'list_data_glifs': [],
    'varShowErrorBars': 0,
    'varShowEllipses': 1

}

