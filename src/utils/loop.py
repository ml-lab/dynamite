import z3

import helpers.vcommon as dig_common_helpers
import data.prog as dig_prog
import settings as dig_settings
from data.prog import Symb, Symbs
from data.traces import Inps, Inp
from helpers.miscs import Z3

from utils import settings
from lib import Classification

mlog = dig_common_helpers.getLogger(__name__, settings.logger_level)

class LoopPart(object):
    def __init__(self, inp_decls, cond, transrel):
        self.inp_decls = inp_decls
        self.cond = cond
        self.transrel = transrel

class Stem(LoopPart):
    def get_initial_cond(self, f, config):
        # init_symvars = (config.symstates.init_symvars).exprs(settings.use_reals)
        init_f = z3.And(self.cond, self.transrel, f)
        # init_f_vars = Z3.get_vars(init_f)
        # exists_vars = init_f_vars.difference(init_symvars)
        # init_cond = z3.Exists(list(exists_vars), init_f)
        # mlog.debug("init_cond: {}".format(init_cond))
        # qe_init_cond = Z3.qe(init_cond)
        # mlog.debug("qe_init_cond: {}".format(qe_init_cond))
        return init_f

    def get_initial_inp(self, inp, config):
        assert isinstance(inp, Inp)
        ss = config.inv_decls[config.preloop_loc]
        # inp_decls = Symbs([Symb(s, 'I' if type(v) is int else 'D') for s, v in zip(inp.ss, inp.vs)])
        inp_f = inp.mkExpr(ss.exprs(settings.use_reals))
        # f = z3.And(self.cond, self.transrel, inp_f)
        f = self.get_initial_cond(inp_f, config)
        # mlog.debug("f: {}".format(f))
        rs, _ = config.solver.get_models(f, 1, settings.use_random_seed)
        # mlog.debug("rs: {}".format(rs))
        init_symvars = config.symstates.init_symvars
        inps = config.solver.mk_inps_from_models(
                    rs, init_symvars.exprs((settings.use_reals)), config.exe)
        inp_ss = tuple([s for (s, _) in self.inp_decls])
        inps = Inps(set(map(lambda inp: Inp(inp_ss, inp.vs), inps)))
        # mlog.debug("inps: {}".format(inps))
        return inps

class Loop(LoopPart):
    pass

class LoopInfo(object):
    def __init__(self, vloop_id, inv_decls, stem=None, loop=None):
        self.stem = stem
        self.loop = loop
        self.vloop_id = vloop_id
        self.inv_decls = inv_decls
        self.vloop_pos = self._get_vloop_pos(vloop_id)
        if self.vloop_pos:
            vloop_postfix = '_' + self.vloop_pos
        else:
            vloop_postfix = ''
        vtrace_loc = lambda i: dig_settings.TRACE_INDICATOR + str(i) + vloop_postfix
        self.preloop_loc = vtrace_loc(settings.VTRACE.PRELOOP_LABEL) # vtrace1
        self.inloop_loc =  vtrace_loc(settings.VTRACE.INLOOP_LABEL) # vtrace2
        self.transrel_loc = vtrace_loc(settings.VTRACE.TRANSREL_LABEL) # vtrace4
        self.postloop_loc = vtrace_loc(settings.VTRACE.POSTLOOP_LABEL) # vtrace3
        self.cl = Classification(self.preloop_loc, self.inloop_loc, self.postloop_loc)
        self.transrel_pre_inv_decls, self.transrel_pre_sst, \
            self.transrel_post_sst, transrel_inv_decls = self._mk_transrel_sst()

    def _get_vloop_pos(self, vloop_id):
        vloop_prefix = settings.VLOOP_FUN + '_'
        if vloop_id.startswith(vloop_prefix):
            return vloop_id[len(vloop_prefix):]
        else:
            return None

    def _mk_transrel_sst(self):
        inloop_inv_decls = self.inv_decls[self.inloop_loc]
        inloop_inv_exprs = inloop_inv_decls.exprs(settings.use_reals)
        transrel_pre_inv_decls = [dig_prog.Symb(s.name + '0', s.typ) for s in inloop_inv_decls]
        transrel_pre_inv_exprs = dig_prog.Symbs(transrel_pre_inv_decls).exprs(settings.use_reals)
        transrel_post_inv_decls = [dig_prog.Symb(s.name + '1', s.typ) for s in inloop_inv_decls]
        transrel_post_inv_exprs = dig_prog.Symbs(transrel_post_inv_decls).exprs(settings.use_reals)

        transrel_inv_decls = dig_prog.Symbs(transrel_pre_inv_decls + transrel_post_inv_decls)

        return transrel_pre_inv_exprs, \
               list(zip(inloop_inv_exprs, transrel_pre_inv_exprs)), \
               list(zip(inloop_inv_exprs, transrel_post_inv_exprs)), \
               transrel_inv_decls