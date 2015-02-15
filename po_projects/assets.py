"""
Asset bundles to use with django-assets
"""
try:
    from django_assets import Bundle, register
except ImportError:
    DJANGO_ASSETS_INSTALLED = False
else:
    DJANGO_ASSETS_INSTALLED = True

    AVALAIBLE_BUNDLES = {
        'po_projects_app_css': Bundle(
            "css/po-projects_app.css",
            filters='yui_css',
            output='css/po-projects_app.min.css'
        ),
        'po_projects_app_js': Bundle(
            "js/po-projects/plugins.js",
            filters='yui_js',
            output='js/po-projects_app.min.js'
        ),
    }

    ENABLED_BUNDLES = (
        'po_projects_app_css',
        'po_projects_app_js',
    )

    for item in ENABLED_BUNDLES:
        register(item, AVALAIBLE_BUNDLES[item])
