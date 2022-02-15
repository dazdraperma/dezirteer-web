from django.urls import path
from .views import index, bokeh, model_form_upload, statistics, StringIODownloadView, session_form_upload, \
    get_keep_prev_data, new_session

app_name = 'main'

urlpatterns = [
    path('', index, name='index'),
    path('bokeh/', bokeh, name='bokeh'),
    path('statistics/', statistics, name='statistics'),
    path('<int:id_sample>/', index, name="select-sample"),
    path('uploads/form/', model_form_upload, name='model_form_upload'),
    path("savesession/", StringIODownloadView.as_view(), name="save-session"),
    path('uploads/sessions/', session_form_upload, name='session-form-upload'),
    path('getkeepprevdata/', get_keep_prev_data, name='get-keep-prev-data'),
    path('newsession/', new_session, name='new-session')
]


