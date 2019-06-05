#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# 14-04-2019
# alex
# solucionador.py

import numpy as np
import time as tm
import os
from ddnls import *
from fluxABC import *
from em_estatic import *

def is_numeric(val):
    if (val.strip() == ""):
        return False
    try:
        float(val)
    except ValueError:
        return False
    else:
        return True
    
def crearDir(met):
    if not os.path.exists("dat"):
        os.mkdir("dat")
    for i in range(0, len(met)):
        direc = "dat/" + met[i]
        if not os.path.exists(direc):
            os.mkdir(direc)

def XaABC_priv(a, ordre):
    A, B, C = ordre
    m = len(a) / 2
    senar = (len(a) % 2) != 0
    metode = []
    cont = [0, 0, 0]
    coef = [[], [], []]
    metode.append([A, cont[A]])
    cont[A] = cont[A] + 1
    coef[A].append(a[0])
    
    for i in range(0, m):
        metode.append([B, cont[B]])
        cont[B] = cont[B] + 1
        metode.append([C, cont[C]])
        cont[C] = cont[C] + 1
        metode.append([B, cont[B]])
        cont[B] = cont[B] + 1
        metode.append([A, cont[A]])
        cont[A] = cont[A] + 1
    if (senar):
        metode.append([B, cont[B]])
        cont[B] = cont[B] + 1
        metode.append([C, cont[C]])
        cont[C] = cont[C] + 1        
    pu = 2*(m - 1)
    if (senar):
        pu = 2*m
    for i in range(0, pu, 2):
        coef[B].append(a[i])
        coef[C].append(a[i] + a[i + 1])
        coef[B].append(a[i + 1])
        coef[A].append(a[i + 1] + a[i + 2])
    if not senar:
        coef[B].append(a[pu])
        coef[C].append(a[pu]+ a[pu + 1])
        coef[B].append(a[pu + 1])
        coef[A].append(a[pu + 1])
    else:
        coef[B].append(a[pu])
        coef[C].append(a[pu])        
    return [metode, coef]

def XaABC(a):
    return XaABC_priv(a, [0, 1, 2])

def XaABC_adj(a):
    return XaABC_priv(a, [2, 1, 0])

def lectura_coefX_priv(nom_fit):
    fit = open("./coef/" + nom_fit + ".cnf", "r")
    lis = fit.readlines()
    fit.close()
    coef = []
    nom = []
    for i, item in enumerate(lis):
        aux = []
        linia = item.replace("\n", "")
        tros = linia.split(" ")
        for j, jtem in enumerate(tros):
            if (is_numeric(jtem)):
                aux.append(float(jtem))
            elif (j == 0):
                nom.append(jtem[0])
        if (len(aux) > 0):
            coef.append(aux)
    return nom, coef

def lectura_coefX(nom_fit):
    vec_coef = lectura_coefX_priv(nom_fit)[1]
    metode, coef = XaABC(vec_coef[0])
    return [metode, coef]

def lectura_coefABC(nom_fit):
    linies = []
    with open("./coef/" + nom_fit + ".cnf") as fit:
        linies = fit.readlines()
    metode = []
    vec_a = []
    vec_b = []
    vec_c = []
    coef = [[], [], []]
    for i in range(0, len(linies)):
        linia = linies[i].replace("\n", "")
        if linia[0] == 'm':
            linia = linia[2:]
            cadena = linia.split(" ")
            for j in range(0, len(cadena)):
                flux = ord(cadena[j][0]) - 97
                nume = int(cadena[j][1]) - 1
                metode.append([flux, nume])
        else:
            ind = ord(linia[0]) - 97
            linia = linia[2:]
            cadena = linia.split(" ")
            for j in range(0, len(cadena)):
                coef[ind].append(float(cadena[j]))
    return [metode, coef]

def lectura_coefX_P1(nom_fit):
    noms, coefs = lectura_coefX_priv(nom_fit)
    tam = len(noms)
    i = 0
    while (i < tam) and (noms[i] != 'a'):
        i = i + 1
    met_a, cof_a = XaABC(coefs[i])
    i = 0
    while (i < tam) and (noms[i] != 'g'):
        i = i + 1
    met_pre, cof_pre = XaABC_adj(coefs[i])
    coefs_p = []
    n = len(coefs[i])
    for j in range(0, n):
        coefs_p.append(-coefs[i][n - j - 1])
    met_pos, cof_pos = XaABC(coefs_p)
    return [met_a, cof_a], [met_pre, cof_pre], [met_pos, cof_pos]

def lectura_coefX_P2(nom_fit):
    noms, coefs = lectura_coefX_priv(nom_fit)
    tam = len(noms)
    i = 0
    while (i < tam) and (noms[i] != 'a'):
        i = i + 1
    met_a, cof_a = XaABC_adj(coefs[i])
    i = 0
    while (i < tam) and (noms[i] != 'g'):
        i = i + 1
    cofX_pre = []
    cofX_pos = []
    n = len(coefs[i])
    for j in range(0, n):
        #cofX_pre.append(-coefs[i][n - j - 1])
        cofX_pos.append(-coefs[i][j])
    for j in range(0, n):
        #cofX_pre.append(coefs[i][n - j - 1])
        cofX_pos.append(coefs[i][j])
    #met_pre, cof_pre = XaABC(cofX_pre)
    for j in range(0, 2*n):
        cofX_pre.append(-cofX_pos[2*n - j - 1])
    met_pos, cof_pos = XaABC(cofX_pre[::-1])
    met_pre, cof_pre = XaABC(cofX_pos[::-1])
    return [met_a, cof_a], [met_pre, cof_pre], [met_pos, cof_pos]

def solucionador(problema, tipus_metode, tipus_processat, metode, h, T, calOrdreQP = False, printZ = False, printC = False):
    if (problema == "ddnls"):
        fluxABC = fluxABCddnls
        iniciador = iniciador_ddnls
        conserves = [funcioS_ddnls, funcioH_ddnls]
        N = 1000
        B = 0.72
        W = 4.0
        e = np.array(np.zeros(N))
        z = np.array(np.zeros(2*N))
        direc = "."
        parametres = [e, B, N, W, direc]
    elif (problema == "fluxABC"):
        iniciador = iniciador_fluxABC
        fluxABC = fluxABC_fluxABC
        conserves = []
        A = 0.5
        B = 1.0
        C = 1.0
        z = np.array(np.zeros(3))
        parametres = [A, B, C]
    elif (problema == "em_estatic"):
        iniciador = iniciador_em_estatic
        fluxABC = fluxABCem_estatic
        conserves = [funcioP_em_estatic, funcioH_em_estatic, funcioMu_em_estatic]
        z = np.array(np.zeros(3*4))
        parametres = [-1.0, 1.0]
    else:
        print "El problema " + problema + " no està definit."
        exit(-1)
    if (tipus_processat == 0):
        if (tipus_metode == 0):
            ordre, coef = lectura_coefX(metode)
        elif (tipus_metode == 1):
            ordre, coef = lectura_coefABC(metode)
        else:
            print str(tipus_metode) + " no és cap tipus de mètode."
            exit(-2)
    elif (tipus_processat == 1):
        if (tipus_metode == 0):
            nucli, prep, postp = lectura_coefX_P1(metode)
            ordre, coef = nucli[0], nucli[1]
            ordre_pre, coef_pre = prep[0], prep[1]
            ordre_pos, coef_pos = postp[0], postp[1]            
        else:
            print "El processat " + str(tipus_processat) + " no està preparat per als mètodes " + str(tipus_metode)
            exit(-2)
    elif (tipus_processat == 2):
        if (tipus_metode == 0):
            nucli, prep, postp = lectura_coefX_P2(metode)
            ordre, coef = nucli[0], nucli[1]
            ordre_pre, coef_pre = prep[0], prep[1]
            ordre_pos, coef_pos = postp[0], postp[1]            
        else:
            print "El processat " + str(tipus_processat) + " no està preparat per als mètodes " + str(tipus_metode)
            exit(-2)

    ruta_comu = "./dat/" + metode + "/" + problema
    ruta_Z = ruta_comu + "_coor_" + str(int(round(T))) + "_" + str(h).replace(".", "") + ".dat"
    ruta_C = ruta_comu + "_cons_" + str(int(round(T))) + "_" + str(h).replace(".", "") + ".dat"
    if printZ:
        fitZ = open(ruta_Z, "w")
    if printC:
        fitC = open(ruta_C, "w")    
    m = len(ordre)
    r = 0
    Nit = int(round(T / h))
    p_it = 0
    if (tipus_processat > 0):
        r = len(ordre_pre)
        p_it = Nit / 5
    temps = 0.0
    Neval = 0
    iniciador(z, parametres)
    num_cons = len(conserves)
    Csub0 = np.array(np.zeros(num_cons))
    Cvalr = np.array(np.zeros(num_cons))
    Cemax = np.array(np.zeros(num_cons))
    Cdife = np.array(np.zeros(num_cons))
    for i in range(0, num_cons):
        Csub0[i] = conserves[i](z, parametres)
        Cvalr[i] = Csub0[i]
    # preprocessat
    if (tipus_processat > 0):
        t0 = tm.time()
        for i in range(0, r):
            flux = ordre_pre[i][0]
            index = ordre_pre[i][1]
            dt = coef_pre[flux][index] * h
            fluxABC(flux, z, dt, parametres)
            temps += tm.time() - t0
        Neval += r
    # nucli
    for it in range(0, Nit):
        t0 = tm.time()
        for i in range(0, m):
            flux = ordre[i][0]
            index = ordre[i][1]
            dt = coef[flux][index] * h
            fluxABC(flux, z, dt, parametres)
        temps += tm.time() - t0
        Neval += m
        if ((tipus_processat > 0) and ((it % p_it == 0) or (it == Nit - 1))) or (tipus_processat == 0):
            z_copia = z.copy()
            t0 = tm.time()
            # post-processat
            for i in range(0, r):
                flux = ordre_pos[i][0]
                index = ordre_pos[i][1]
                dt = coef_pos[flux][index] * h
                fluxABC(flux, z, dt, parametres)
            temps += tm.time() - t0
            Neval += r
            # càlcul de les quantitats conservades
            for i in range(0, num_cons):
                Cvalr[i] = conserves[i](z, parametres)
                Cdife[i] = abs(Cvalr[i] - Csub0[i])
                if (Cdife[i] > Cemax[i]):
                    Cemax[i] = Cdife[i]
            # imprimir z i quantitats conservades
            if printZ:
                esc = str(it * h) + " " + str(z.tolist()).replace(",", "").replace("[", "").replace("]","")
                fitZ.write(esc + "\n")
            if printC:
                esc = str(it * h) + " "
                for i in range(0, num_cons):
                    esc = esc + " " + str(Cvalr[i]) + " " +  str(Cdife[i]/Csub0[i])
                fitC.write(esc + "\n")
            if (it < Nit - 1):
                z = z_copia.copy()
    
    tornar = [temps, Neval]
    for i in range(0, num_cons):
        tornar.append(abs(Cemax[i]/Csub0[i]))
        
    if printZ:
        fitZ.close()
    if printC:
        fitC.close()
    # comparació amb la solució exacta
    if (calOrdreQP == True):
        ruta_ex = "./dat/dop853/" + problema + "_t" + str(int(round(T))) + ".dat"
        errorQP = 0.0
        with open(ruta_ex) as fit:
            linies = fit.readlines()
            num = 0.0
            den = 0.0
            for i in range(0, len(linies)):
                lin_net = linies[i].replace(",", "").replace("\n", "")
                lin = lin_net.split(" ")
                z_ex = float(lin[1])
                num = num + (z[i] - z_ex)**2
                den = den + z_ex**2
            errorQP = np.sqrt(num / den)
        tornar.append(errorQP)
    return tornar

def sol_exacte(problema, t0, tf):
    t = t0
    h = tf - t0
    if (problema == "ddnls"):
        iniciador = iniciador_ddnls
        eqDreta = eqDreta_ddnls
        N = 1000
        B = 0.72
        W = 4.0
        e = np.array(np.zeros(N))
        z = np.array(np.zeros(2*N))
        direc = "."
        parametres = [e, B, N, W, direc]
    elif (problema == "fluxABC"):
        iniciador = iniciador_fluxABC
        eqDreta = eqDreta_fluxABC
        A = 0.5
        B = 1.0
        C = 1.0
        z = np.array(np.zeros(3))
        parametres = [A, B, C]
    elif (problema == "em_estatic"):
        iniciador = iniciador_em_estatic
        eqDreta = eqDreta_em_estatic
        z = np.array(np.zeros(3*4))
        parametres = [-1.0, 1.0]
    else:
        print "El métode " + problema + " no està definit."
        exit(-3)
        
    iniciador(z, parametres)
    solver = ode(eqDreta)
    solver.set_integrator('dop853', rtol = 1e-15, nsteps = 5000)
    solver.set_f_params(parametres)
    solver.set_initial_value(z, t)
    while solver.successful() and solver.t < tf:
        t = t + h
        solver.integrate(t)
    if (solver.t != tf):
        print "No s'ha pogut evolucionar fins", tf, "només fins", solver.t
        exit(-1)
    return solver.y

if __name__ == "__main__":
    # print solucionador("fluxABC", 0, 0, "tc_6_8", 0.5, 10, True)
    # print solucionador("ddnls", 1, 0, "abc_4", 0.05, 10, True, True, True)
    # print solucionador("fluxABC", 0, 0, "tc_4_1", 0.5, 10, True)
    # print solucionador("fluxABC", 0, 1, "psx_4_4_4", 0.5, 10, True)
    # print solucionador("fluxABC", 0, 2, "pc_6_3_4", 0.5, 10, True)
    # print solucionador("fluxABC", 0, 1, "psx_4_4_4", 0.5, 10, True)
    # print solucionador("fluxABC", 0, 2, "pc_6_3_4", 0.5, 10, True)
    # print solucionador("fluxABC", 0, 1, "psx_4_4_4", 0.05, 10, True)
    # print solucionador("fluxABC", 0, 2, "pc_6_3_4", 0.05, 10, True)
    print solucionador("em_estatic", 0, 0, "tc_6_6", np.pi/100.0, 1000, True, True, True)