from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myproject.views.home', name='home'),
    # url(r'^myproject/', include('myproject.foo.urls')),
    #url(r'^favicon.\ico$', 'django.views.generic.simple.redirect_to', {'url': '/media/images/favicon.ico'}),
    url(r'^$', 'app.views.index'),
    url(r'^m/', 'app.views.home'),
    url(r'^trial/', 'app.views.home'),
    url(r'^rewards/', 'app.views.rewards'),
    #url(r'', 'app.views.home'),
    url(r'^apicallback/', 'app.views.apicallback'),
    url(r'^ajax_email/', 'app.views.ajax_put_email'),
    url(r'^activation/(?P<activation_code>\w+)/$', 'app.views.activation'),
    url(r'^ajax_send_reward/', 'app.views.ajax_send_reward'),
    url(r'^tos/', 'app.views.tos'),
    url(r'^not_allowed/', 'app.views.not_allowed'),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
