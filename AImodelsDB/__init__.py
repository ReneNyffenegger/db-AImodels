# vim: foldmethod=marker foldmarker={{{,}}}

import RenesSQLiteHelper as db

def open_AImodels_db(deleteIfExists = False):
    con = db.open_db('AImodels', deleteIfExists = deleteIfExists)
    return con
