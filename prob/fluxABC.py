#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# 16-04-2019
# alex
# fluxABC.py

import numpy as np

def ini_fluxABC(z, params):
    A, B, C = params
    z[0] = 3.14
    z[1] = 2.77
    z[2] = 0.0

def mapaABC_fluxABC(flux, z, h, params):
    A, B, C = params
    # z[flux] = z[flux] + h*(params[(flux + 1)%3]*np.cos(z[(flux + 1)%3]) + params[(flux + 2)%3]*np.sin(z[(flux + 2)%3]))
    if flux == 0:
        z[0]= z[0]
        z[1]= z[1] + h*A*np.sin(z[0])
        z[2]= z[2] + h*A*np.cos(z[0])      
    elif flux == 1:
        z[0]= z[0] + h*B*np.cos(z[1])
        z[1]= z[1]
        z[2]= z[2] + h*B*np.sin(z[1])
    elif flux == 2:
        z[0]= z[0] + h*C*np.sin(z[2])
        z[1]= z[1] + h*C*np.cos(z[2])
        z[2]= z[2] 

def eqDreta_fluxABC(t, z, params):
    A, B, C = params
    xx, yy, zz = z[0], z[1], z[2]
    xpunt = B*np.cos(yy) + C*np.sin(zz)
    ypunt = C*np.cos(zz) + A*np.sin(xx)
    zpunt = A*np.cos(xx) + B*np.sin(yy)    
    return np.array([xpunt, ypunt, zpunt])
