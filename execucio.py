#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# 24-02-2019
# alex
# execucio.py

import numpy as np
from pymplectic import *
from ddnls import *
from fluxABC import *
from em_estatic import *

if __name__ == "__main__":
    # DDNLS
    ddnls = Solucionador()
    ddnls.set_nom("ddnls")
    ddnls.set_iniciador(iniciador_ddnls)
    ddnls.set_mapa(fluxABCddnls)
    Ndd = 1000
    e = np.array(np.zeros(Ndd))
    ddnls.init_coord(2*Ndd)
    ddnls.add_conserva(funcioS_ddnls)
    ddnls.add_conserva(funcioH_ddnls)
    ddnls.set_parametres([e, 0.72, Ndd, 4.0, "."])
    ddnls.set_calc_error_coord(True)
    ddnls.set_print_coord(False)
    ddnls.set_print_cons(True)
    # Flux ABC
    
    # Particules carregades. Camp em estatic
    em_es = Solucionador()
    em_es.set_nom("em_estatic")
    em_es.set_iniciador(iniciador_em_estatic)
    em_es.init_coord(12)
    em_es.set_mapa(fluxABCem_estatic)
    em_es.set_eqDreta(eqDreta_em_estatic)
    em_es.set_parametres([-1.0, 1.0])
    em_es.add_conserva(funcioP_em_estatic)
    em_es.add_conserva(funcioH_em_estatic)
    em_es.add_conserva(funcioMu_em_estatic)
    em_es.set_calc_error_coord(True)
    em_es.set_print_coord(True)
    em_es.set_print_cons(True)

    prob = ddnls
    t_final = 10.0
    met = []
    tip = []
    pro = []
    h = []
    h_elem = [0.5, 0.4, 0.25, 0.1, 0.05]
    # h_elem = [0.25, 0.1, 0.05, 0.04, 0.025, 0.01, 0.005]
    met.append("abc_4")
    tip.append(1)
    pro.append(0)
    h.append(h_elem)
    
    met.append("tc_5")
    tip.append(0)
    pro.append(0)
    h.append(h_elem)
    
    met.append("tc_5_1")
    tip.append(0)
    pro.append(0)
    h.append(h_elem)    
    
    met.append("tc_5_2")
    tip.append(0)
    pro.append(0)
    h.append(h_elem)
    
    met.append("sx_6_4")
    tip.append(0)
    pro.append(0)
    h.append(h_elem)

    met.append("tc_6_3")
    tip.append(0)
    pro.append(0)
    h.append(h_elem)

    met.append("tc_6_6")
    tip.append(0)
    pro.append(0)
    h.append(h_elem)

    met.append("psx_4_4_4")
    tip.append(0)
    pro.append(1)
    h.append(h_elem)

    met.append("pc_6_6_4")
    tip.append(0)
    pro.append(2)
    h.append(h_elem)

    met.append("pc_9_8_6")
    tip.append(0)
    pro.append(2)
    h.append(h_elem)

    met.append("pc_10_18_6")
    tip.append(0)
    pro.append(2)
    h.append(h_elem)   
    
    
    crearDir(met)
    for i in range(0, len(met)):
        print met[i]
        direc = "dat/" + met[i]
        fit = open(direc + "/" + prob.get_nom() + "_err.dat", "w")
        metode = Metode(tip[i], pro[i])
        metode.set_metode(met[i])
        prob.set_metode(metode)
        for j in range(0, len(h[i])):
            r = prob.solucionar(h[i][j], t_final)
            esc = str(r).replace(",", "").replace("[", "").replace("]","")
            esc = str(h[i][j]) + " " + esc
            fit.write(esc + "\n")
            print esc
        fit.close()