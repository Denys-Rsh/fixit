{
    "name": "Fixit",
    "summary": "Service Center: Tracking Equipment Repairs",
    "description": "Service Center: Tracking Equipment Repairs",
    "author": "Denys Rsh",
    "maintainer": "Denys Rsh",
    "category": "",
    "version": "19.0.1.0.0",
    "license": "OPL-1",
    "images": ["static/description/banner.png"],
    "application": True,
    "installable": True,

    "depends": ["base"],

    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/order_views.xml",
        "views/order_line_views.xml",
        "views/client_views.xml",
        "views/repairman_views.xml",
        "views/part_views.xml",
    ],

    "demo": []
}