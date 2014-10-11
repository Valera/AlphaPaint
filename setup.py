__author__ = 'vfedotov'

from celerid.support import setup, Extension

projName = 'paint_engine_core'

setup(
    name=projName,
    version='0.1',
    ext_modules=[
    Extension(projName, sources=['paint_engine_core/paint_engine_core/engine.d',
                                 'paint_engine_core/paint_engine_core/python_export.d',
                                 'paint_engine_core/paint_engine_core/brush.d'],
        build_deimos=True,
        d_lump=True
        )
    ],
)