#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/home/hengji/Documents/hydra_calcium_model/current/single/')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.sparse import spdiags
# from young_keizer_cell import DeYoungKeizerCell
# from fast_cell import FastCell
from cell import Cell

class Chain(Cell):
    '''A 1D cell chain with cells connected through gap junctions'''
    def __init__(self, num=20, T=20):
        # Parameters
        super().__init__(T)
        self.gc = 5e4
        self.g_ip3 = 1 # 2 
        self.num = num
        onex = np.ones(self.num)
        self.Dx = spdiags(np.array([onex,-2*onex,onex]),np.array([-1,0,1]),self.num,self.num).toarray()
        self.Dx[0,0] = -1
        self.Dx[self.num-1,self.num-1] = -1 
        self.k9 = 0.04

    def stim(self, t):
        # Stimulation
        if 20 <= t < 24:
            return 1
        else:
            return self.v8

    def stim_v(self, t):
        # Stimulation

        if 101 <= t < 101.01 or 103 <= t < 103.01 or 105 <= t < 105.01 \
            or 109 <= t < 109.01 or 113 <= t < 113.01 or 117 <= t < 117.01 or 121 <= t < 121.01 \
            or 125 <= t < 125.01 \
            or 130 <= t < 130.01 or 135 <= t < 135.01 or 140 <= t < 140.01 \
            or 145 <= t < 145.01 or 150 <= t < 150.01 or 155 <= t < 155.01 or 160 <= t < 160.01 \
            or 166 <= t < 166.01 or 172 <= t < 172.01:
            return 1
        else:
            return 0
    
    def rhs(self, y, t):
        # Right-hand side formulation
        num = self.num

        c, s, r, ip, v, n, hv, hc, x, z, p, q = (y[0:num], y[num:2*num], 
        y[2*num:3*num], y[3*num:4*num], y[4*num:5*num], 
        y[5*num:6*num], y[6*num:7*num], y[7*num:8*num], 
        y[8*num:9*num], y[9*num:10*num], y[10*num:11*num], 
        y[11*num:12*num])

        dcdt = self.i_rel(c, s, ip, r) + self.i_leak(c, s) - self.i_serca(c) + self.i_in() - self.i_pmca(c) - self.i_out(c)\
            - 1e9 * self.i_cal(v, n, hv, hc) / (2 * self.F * self.d)
        dsdt = self.beta * (self.i_serca(c) - self.i_rel(c, s, ip, r) - self.i_leak(c, s))
        drdt = self.v_r(c, r)
        dipdt = self.i_plcb(self.v8) + self.i_plcd(c) - self.i_deg(ip) + self.g_ip3 * self.Dx@ip
        dipdt[0:3] += self.i_plcb(self.stim(t)) - self.i_plcb(self.v8)
        dvdt = - 1 / self.c_m * (self.i_cal(v, n, hv, hc) + self.i_kcnq(v, x, z) + self.i_kv(v, p, q) + self.i_bk(v)) + self.gc * self.Dx@v
        dvdt[0:3] += 1 / self.c_m * 0.1 * self.stim_v(t)
        dndt = (self.n_inf(v) - n)/self.tau_n(v)
        dhvdt = (self.hv_inf(v) - hv)/self.tau_hv(v)
        dhcdt = (self.hc_inf(c) - hc)/self.tau_hc()
        dxdt = (self.x_inf(v) - x)/self.tau_x(v)
        dzdt = (self.z_inf(v) - z)/self.tau_z(v)
        dpdt = (self.p_inf(v) - p)/self.tau_p(v)
        dqdt = (self.q_inf(v) - q)/self.tau_q(v)

        deriv = np.array([dcdt, dsdt, drdt, dipdt, dvdt, dndt, dhvdt, dhcdt, dxdt, dzdt, dpdt, dqdt])

        dydt = np.reshape(deriv, 12*num)

        return dydt

    def step(self):
        # Time stepping

        self.v8 = (self.i_deg(self.ip0) - self.i_plcd(self.c0)) / (1 / ((1 + self.kg)*(self.kg/(1+self.kg) + self.a0)) * self.a0)

        y0 = np.array([[self.c0]*self.num, 
                       [self.s0]*self.num, 
                       [self.r0]*self.num, 
                       [self.ip0]*self.num,
                       [self.v0]*self.num,
                       [self.n0]*self.num,
                       [self.hv0]*self.num,
                       [self.hc0]*self.num,
                       [self.x0]*self.num,
                       [self.z0]*self.num,
                       [self.p0]*self.num,
                       [self.q0]*self.num,])

        y0 = np.reshape(y0, 12*self.num)
        
        sol = odeint(self.rhs, y0, self.time, hmax = 0.005)
        return sol

    def plot(self, a, tmin=0, tmax=200, xlabel = 'time[s]', ylabel = None):
        # Plot function
        plt.plot(self.time[int(tmin/self.dt):int(tmax/self.dt)], a[int(tmin/self.dt):int(tmax/self.dt)])
        if xlabel:  plt.xlabel(xlabel)
        if ylabel:  plt.ylabel(ylabel)

if __name__ == "__main__":

    n_cel = 20

    model = Chain(n_cel, 200)
    sol = model.step()
    c = sol[:,0:n_cel]
    s = sol[:,n_cel:2*n_cel]
    r = sol[:,2*n_cel:3*n_cel]
    ip = sol[:,3*n_cel:4*n_cel]
    v = sol[:, 4*n_cel:5*n_cel]

    # Plot the results
    plt.figure()
    plt.subplot(221)
    model.plot(c, ylabel = 'c[uM]')
    plt.subplot(222)
    model.plot(s, ylabel = 'c_ER[uM]')
    plt.subplot(223)
    model.plot(v, ylabel = 'v[mV]')
    plt.subplot(224)
    model.plot(ip, ylabel = 'IP3[uM]')
    plt.show()

    # Save the [Ca2+]
    df = pd.DataFrame(sol[:,0:n_cel])
    df.to_csv('../save/data/c_20x1_200s.csv', index = False)

    



