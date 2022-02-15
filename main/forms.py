from crispy_forms.bootstrap import InlineRadios, FormActions, StrictButton
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div, Fieldset, Button, Hidden
from django.utils.safestring import mark_safe

from main.const import EarthAge


# from main.models import Document


# class DocumentForm(forms.ModelForm):
#     class Meta:
#         model = Document
#         fields = ('description', 'document', )


class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))


class UploadFileSessionForm(forms.Form):
    file = forms.FileField()


class SettingsForm(forms.Form):
    uncType = forms.TypedChoiceField(
        label=mark_safe("<strong>Uncertainty type:</strong>"),
        choices=(
            ('1', "Int"),
            ('2', "Prop")
        ),
        # coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        initial='1',
        required=False,
    )
    lboxSamples = forms.MultipleChoiceField(
        label=mark_safe("<strong>Samples:</strong>"),
        widget=forms.SelectMultiple,
        required=False,
    )

    # ===================================
    cbWhichAge = forms.ChoiceField(
        label=mark_safe("<strong>How to calc best age:</strong>"),
        choices=(('0', 'From lesser error'), ('1', 'Fixed Limit'), ('2', '207Pb/206Pb'), ('3', '206Pb/238U')),
        widget=forms.Select(),
        initial='0',
        required=False,

    )

    entAgeCutoff = forms.DecimalField(
        label=mark_safe("<strong>Ma:</strong>"),
        min_value=0,
        max_value=EarthAge,
        widget=forms.NumberInput(attrs={'readonly': True}),
        initial=1000,
        required=False,

    )

    # ===================================
    cbPbc = forms.ChoiceField(
        label=mark_safe("<strong>Use common Pb corr. ages?:</strong>"),
        choices=(('0', 'No'), ('1', '204Pbc'), ('2', '207Pbc'), ('3', '208Pbc'), ('4', 'Ander.')),
        widget=forms.Select,
        required=False,
        initial='0',

    )
    entAgeAndersen = forms.DecimalField(
        label=mark_safe("<strong>And.Ma:</strong>"),
        min_value=0,
        max_value=EarthAge,
        widget=forms.NumberInput(attrs={'readonly': True}),
        required=False,
        initial=0,
    )

    # ===================================
    cbWhichConc = forms.ChoiceField(
        label=mark_safe("<strong>How to calc discordance:</strong>"),
        choices=(('0', 'Fixed limit (Ma):'), ('1', '207/206-206/238'), ('2', '207/235-206/238'), ('3', 'Lesser of 2')),
        widget=forms.Select,
        required=False,
        initial='3',
    )
    entDiscAgeFixedLim = forms.DecimalField(
        label=mark_safe("<strong>Ma:</strong>"),
        min_value=0,
        max_value=EarthAge,
        widget=forms.NumberInput(attrs={'readonly': True}),
        required=False,
        initial=1000,
    )

    # ============ Filter =======================
    rbDiscPerc = forms.TypedChoiceField(
        label=mark_safe("<strong>Filters:</strong>"),
        choices=(
            ('0', "EITHER: Filter out high discord. values(%)"),
            ('1', "OR: Filter out if miss concordia within uncertainty:")
        ),
        # coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        initial='0',
        required=False,
    )
    entNegDiscFilt = forms.DecimalField(
        label=mark_safe("<strong>(-):</strong>"),
        min_value=0,
        widget=forms.NumberInput,
        required=False,
        initial=10,
    )
    entPosDiscFilt = forms.DecimalField(
        label=mark_safe("<strong>(+):</strong>"),
        min_value=0,
        widget=forms.NumberInput,
        required=False,
        initial=20,
    )
    cbDiscIntersect = forms.ChoiceField(
        label=mark_safe("<strong>(σ):</strong>"),
        choices=(
            ('0', "1σ"),
            ('1', "2σ"),
            ('2', "3σ"),
            ('3', "4σ"),
            ('4', "5σ"),
            ('5', "6σ"),
            ('6', "7σ"),
            ('7', "8σ"),
            ('8', "9σ"),
            ('9', "10σ"),

        ),
        widget=forms.Select(attrs={'disabled': True}),
        required=False,
        initial='0'

    )
    cbErrFilter = forms.ChoiceField(
        label=mark_safe("<strong>Filter by error:</strong>"),
        choices=(('0', 'Not used'), ('1', 'Used')),
        widget=forms.Select,
        required=False,
        initial='0',
    )
    entErrFilter = forms.DecimalField(
        label=mark_safe("<strong>%:</strong>"),
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'readonly': True}),
        required=False,
        initial=5,
    )
    cbUConc = forms.ChoiceField(
        label=mark_safe("<strong>Filter by Uconc:</strong>"),
        choices=(('0', 'Not used'), ('1', 'Used')),
        widget=forms.Select,
        required=False,
        initial='0',
    )
    entUconcCutoff = forms.DecimalField(
        label=mark_safe("<strong>ppm:</strong>"),
        min_value=0,
        max_value=1000000,
        widget=forms.NumberInput(attrs={'readonly': True}),
        required=False,
        initial=1000,
    )

    chbInclude207235Err = forms.BooleanField(
        label='include 7/5 error',
        widget=forms.CheckboxInput(attrs={'disabled': True}),
        required=False,
        initial=False)

    # ============ Graph Settings =======================
    cbConcType = forms.ChoiceField(
        label=mark_safe("<strong>Conc. type:</strong>"),
        choices=(('0', 'Standard'), ('1', 'Tera-Wass.')),
        widget=forms.Select,
        required=False,
        initial='0'
    )
    cbEllipsesAt = forms.ChoiceField(
        label=mark_safe("<strong>Ellipses at:</strong>"),
        choices=(('0', '1σ'), ('1', '2σ')),
        widget=forms.Select,
        required=False,
        initial='0'
    )
    cbShowUncorrCorrBothEllipses = forms.ChoiceField(
        label=mark_safe("<strong>204Pbc ellipses?:</strong>"),
        choices=(('0', 'Uncorr'), ('1', '204Pb-corr.'), ('2', 'Both')),
        widget=forms.Select,
        required=False,
        initial='0'
    )

    chbIncludeBadEllipses = forms.BooleanField(
        label="show bad spots",
        widget=forms.CheckboxInput(),
        required=False,
        initial=False
    )

    cbDensityPlotType = forms.ChoiceField(
        label=mark_safe("<strong>Type:</strong>"),
        choices=(('0', 'KDE'), ('1', 'PDP'), ('2', 'Histogram')),
        widget=forms.Select,
        required=False,
        initial='0'
    )
    entKDEBandwidth = forms.DecimalField(
        label=mark_safe("<strong>Bandwidth:</strong>"),
        min_value=0,
        widget=forms.NumberInput,
        required=False,
        initial=50
    )
    entHistBinwidth = forms.DecimalField(
        label=mark_safe("<strong>Binwidth:</strong>"),
        min_value=0,
        widget=forms.NumberInput(attrs={'readonly': True}),
        required=False,
        initial=50
    )

    chbMinAgeCrop = forms.BooleanField(
        label=mark_safe("<strong>Min. age:</strong>"),
        widget=forms.CheckboxInput(),
        required=False,
        initial=False
    )

    entAgeMinCrop = forms.DecimalField(
        label="",
        min_value=0,
        widget=forms.NumberInput(attrs={'readonly': True}),
        required=False,
        initial=1
    )

    chbMaxAgeCrop = forms.BooleanField(
        label=mark_safe("<strong>Max. age:</strong>"),
        widget=forms.CheckboxInput(),
        required=False,
        initial=False
    )

    entAgeMaxCrop = forms.DecimalField(
        label="",
        min_value=0,
        widget=forms.NumberInput(attrs={'readonly': True}),
        required=False,
        initial=1
    )

    chbShowCalc = forms.BooleanField(
        label="Show peaks and stat.",
        widget=forms.CheckboxInput(),
        required=False,
        initial=False
    )

    chbKeepPrev = forms.BooleanField(
        label="Keep prev.",
        widget=forms.CheckboxInput(),
        required=False,
        initial=False)

    chbLimitAgeSpectrum = forms.BooleanField(
        label="Zoom to ages",
        widget=forms.CheckboxInput(),
        required=False,
        initial=False)

    chbShowErrorBars = forms.BooleanField(
        label="show error bars",
        widget=forms.CheckboxInput(),
        required=False,
        initial=False)

    chbShowEllipses = forms.BooleanField(
        label="show spots",
        widget=forms.CheckboxInput(),
        required=False,
        initial=True)

    # class Meta:
    #     model = SettingsModel
    #     fields = '__all__'

    def __init__(self, *args, **kwargs):
        self._list_samples = kwargs.pop('list_samples', None)
        super().__init__(*args, **kwargs)
        #        self.fields['lboxSamples'].choices = self._list_samples

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'id_frm'
        self.helper.disable_csrf = True

        self.helper.attrs = {
            'novalidate': ''
        }
        # self.helper.form_id = 'id_frm'

        self.helper.layout = Layout(
            Row(
                # Column(
                #
                #     Div(
                #         Div(
                #             HTML("""
                #          <div id="status" class="alert {{ status_alert }} p-1 m-1">
                #             <strong>Status: </strong>{{ status_text }}
                #         </div>
                #                 """),
                #             Div(InlineRadios('uncType'), css_id='id_uncType'),
                #             Div('lboxSamples', css_class='h-100'),
                #             css_class='card-body'
                #         ),
                #         css_class='card h-100 mb-4'
                #     ),
                # ),

                Column(
                    Div(
                        Div(
                            HTML("""
                                    <strong>Status: </strong> <p id="status" class="text-success">{{ status_text }}</p>
                                        """),
                            Div(InlineRadios('uncType'), css_id='id_uncType'),
                            # InlineRadios('uncType', css_id='id_uncType'),
                            Div('lboxSamples', css_class='h-100'),
                            css_class='card-body h-100'
                        ),
                        Div(

                            Row(
                                Column('cbWhichAge'),
                                Column('entAgeCutoff'),
                                css_class='form-row  p-1'
                            ),
                            Row(
                                Column('cbPbc'),
                                Column('entAgeAndersen'),
                                css_class='form-row'
                            ),
                            Row(
                                Column('cbWhichConc'),
                                Column('entDiscAgeFixedLim'),
                                css_class='form-row'
                            ),
                            css_class='card-body h-100'
                        ),

                        css_class='card h-100 mb-4'
                    ),
                ),

                Column(
                    Div(
                        Div(
                            Div(InlineRadios('rbDiscPerc'), css_id='id_rbDiscPerc'),
                            Row(
                                Column('entNegDiscFilt'),
                                Column('entPosDiscFilt'),
                                Column('cbDiscIntersect'),
                                # Hidden('cbDiscIntersect', '0'),
                                css_class='form-row'
                            ),
                            Row(
                                Column('cbErrFilter'),
                                Column('entErrFilter'),
                                css_class='form-row'
                            ),
                            Div('chbInclude207235Err'),
                            Row(
                                Column('cbUConc'),
                                Column('entUconcCutoff'),
                                css_class='form-row'
                            ),
                            css_class='card-body h-100'
                        ),
                        css_class='card h-100 mb-4'
                    ),
                ),
                Column(
                    Div(
                        Div(
                            Row(
                                Column('cbConcType'),
                                Column('cbEllipsesAt'),
                                css_class='form-row'
                            ),
                            Row(
                                Column('cbShowUncorrCorrBothEllipses'),
                                Column('chbShowEllipses', 'chbIncludeBadEllipses', 'chbShowErrorBars'),
                                css_class='form-row'
                            ),
                            Div('cbDensityPlotType'),
                            Row(
                                Column('entKDEBandwidth'),
                                Column('entHistBinwidth'),
                                css_class='form-row'
                            ),
                            Row(
                                Column('chbMinAgeCrop'),
                                Column('entAgeMinCrop'),
                                Column('chbMaxAgeCrop'),
                                Column('entAgeMaxCrop'),
                                css_class='form-row'
                            ),
                            Row(
                                Column('chbShowCalc'),
                                Column('chbKeepPrev'),
                                Column('chbLimitAgeSpectrum'),
                                css_class='form-row'
                            ),
                            css_class='card-body h-100'
                        ),
                        css_class='card h-100 mb-4'
                    ),

                    # FormActions(
                    #     # Submit('main:export', 'Export', css_id="ajax_export"),
                    #     # Submit('main:clear', 'Clear', css_id="ajax_clear"),
                    #     Row(
                    #         Column(Submit('main:stat', 'Stat', css_id="ajax_stat", css_class="btn btn-warning",
                    #                       style="width:100%; height:100%")),
                    #         Column(Submit('main:bokeh', 'Plot', css_id="ajax_bokeh", ss_class="btn btn-success",
                    #                       style="width:100%; height:100%")),
                    #     )
                    # ),

                )
            ),

        )
