# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 13:02:59 2020

@author: sasha

Library for drawing standard junctions and other relevant components (contact tabs, etc)
"""

import maskLib.MaskLib as m
from dxfwrite import DXFEngine as dxf
from dxfwrite import const

from dxfwrite.vector2d import vadd, midpoint ,vsub, vector2angle, magnitude, distance
from dxfwrite.algebra import rotate_2d

from maskLib.Entities import SolidPline, SkewRect, CurveRect, InsideCurve

import math

# ===============================================================================
# contact pad functions (for ground plane)
# ===============================================================================

def JContact_slot(chip,structure,rotation=0,gapw=3,gapl=0,tabw=2,tabl=0,taboffs=0,r_out=None,r_ins=None,ptDensity=60,hflip=False,bgcolor=None,debug=False,**kwargs):
    '''
    Creates shapes forming a negative space puzzle piece slot (tab) with rounded corners, and adjustable angles. 
    No overlap : XOR mode compatible
    Centered on outside midpoint of gap
    
    gap: {width (gapw),height (gapl),r_out}
    tab: {slot width, (tabw),height (tabl), height offset (taboffs),r_ins}

    '''
    def struct():
        if isinstance(structure,m.Structure):
            return structure
        elif isinstance(structure,tuple):
            return m.Structure(chip,start=structure,direction=rotation)
        else:
            return chip.structure(structure)
    if r_out is None:
        try:
            r_out = struct().defaults['r_out']
        except KeyError:
            #print('\x1b[33mr_out not defined in ',chip.chipID,'!\x1b[0m')
            r_out = 0
    if r_ins is None:
        try:
            r_ins = struct().defaults['r_ins']
        except KeyError:
            #print('\x1b[33mr_out not defined in ',chip.chipID,'!\x1b[0m')
            r_ins = 0
    if bgcolor is None:
        bgcolor = chip.wafer.bg()
    
    tot_length=2*r_out+gapl+taboffs+2*r_ins+tabl
    half_width=gapw/2+r_out+tabw+r_ins
    
    if hflip:
        struct().shiftPos(tot_length,angle=180)
    
    if taboffs==0:
        theta=90
    else:
        theta = math.degrees(math.atan2(
            (r_ins + r_out)*(taboffs + r_ins + r_out)+ abs(tabw)*math.sqrt(tabw**2 + taboffs*(taboffs + 2*(r_ins + r_out))),
            tabw*(-r_ins - r_out)+(taboffs + r_ins + r_out)*math.sqrt(tabw**2 + taboffs*(taboffs + 2*(r_ins + r_out)))*abs(tabw)/tabw))
    inside_ptx = tot_length-tabl-r_ins*(1+math.sin(math.radians(theta))- (1- math.cos(math.radians(theta)))/math.tan(math.radians(theta)))
    
    chip.add(SolidPline(struct().getPos(),rotation=struct().direction,points=[(gapl+r_out,gapw/2+r_out),
                                                                              (gapl+r_out*(1+math.sin(math.radians(theta))),gapw/2+r_out*(1-math.cos(math.radians(theta)))),
                                                                              (inside_ptx,half_width),(0,half_width),(0,gapw/2+r_out)],bgcolor=bgcolor,**kwargs))
    chip.add(SolidPline(struct().getPos(),rotation=struct().direction,points=[(gapl+r_out,-gapw/2-r_out),
                                                                              (gapl+r_out*(1+math.sin(math.radians(theta))),-gapw/2-r_out*(1-math.cos(math.radians(theta)))),
                                                                              (inside_ptx,-half_width),(0,-half_width),(0,-gapw/2-r_out)],bgcolor=bgcolor,**kwargs))
    
    if r_out>0:
        if debug:
            chip.add(dxf.circle(r_out,struct().getPos((r_out+gapl,gapw/2+r_out)),layer='FRAME',**kwargs))
            chip.add(dxf.circle(r_out,struct().getPos((r_out+gapl,-gapw/2-r_out)),layer='FRAME',**kwargs))
        chip.add(CurveRect(struct().getPos((r_out,gapw/2+r_out)), r_out, r_out,ralign=const.TOP,hflip=True,vflip=True,rotation=struct().direction,bgcolor=bgcolor, **kwargs))
        chip.add(CurveRect(struct().getPos((r_out,-gapw/2-r_out)), r_out, r_out,ralign=const.TOP,hflip=True,rotation=struct().direction,bgcolor=bgcolor, **kwargs))
        if gapl > 0:
            chip.add(dxf.rectangle(struct().getPos((r_out,gapw/2)),gapl,r_out,rotation=struct().direction,bgcolor=bgcolor,**kwargs))
            chip.add(dxf.rectangle(struct().getPos((r_out,-gapw/2)),gapl,-r_out,rotation=struct().direction,bgcolor=bgcolor,**kwargs))
        chip.add(CurveRect(struct().getPos((r_out+gapl,gapw/2+r_out)), r_out, r_out,ralign=const.TOP,angle=theta,vflip=True,rotation=struct().direction,bgcolor=bgcolor, **kwargs))
        chip.add(CurveRect(struct().getPos((r_out+gapl,-gapw/2-r_out)), r_out, r_out,ralign=const.TOP,angle=theta,rotation=struct().direction,bgcolor=bgcolor, **kwargs))
    
    if r_ins>0:
        if debug:
            chip.add(dxf.circle(r_ins,struct().getPos((tot_length-r_ins-tabl,half_width-r_ins)),layer='FRAME',**kwargs))
            chip.add(dxf.circle(r_ins,struct().getPos((tot_length-r_ins-tabl,-half_width+r_ins)),layer='FRAME',**kwargs))
        chip.add(InsideCurve(struct().getPos((tot_length,half_width)), r_ins, rotation=struct().direction,bgcolor=bgcolor,**kwargs))
        chip.add(InsideCurve(struct().getPos((tot_length,-half_width)), r_ins, vflip=True,rotation=struct().direction,bgcolor=bgcolor,**kwargs))
        
        chip.add(InsideCurve(struct().getPos((inside_ptx,half_width)), r_ins,angle=180-theta,hflip=True, rotation=struct().direction,bgcolor=bgcolor,**kwargs))
        chip.add(InsideCurve(struct().getPos((inside_ptx,-half_width)), r_ins,angle=180-theta,hflip=True, vflip=True,rotation=struct().direction,bgcolor=bgcolor,**kwargs))
    
    if hflip:
        struct().shiftPos(0,angle=180)
    else:
        struct().shiftPos(tot_length)
    
    #chip.add(CurveRect(struct().start,s,radius,angle=angle,ptDensity=ptDensity,roffset=w/2,ralign=const.BOTTOM,rotation=struct().direction,vflip=not CCW,bgcolor=bgcolor,**kwargs))
    #chip.add(CurveRect(struct().start,s,radius,angle=angle,ptDensity=ptDensity,roffset=-w/2,ralign=const.TOP,valign=const.TOP,rotation=struct().direction,vflip=not CCW,bgcolor=bgcolor,**kwargs))
    #struct().updatePos(newStart=struct().getPos((radius*math.sin(math.radians(angle)),(CCW and 1 or -1)*radius*(math.cos(math.radians(angle))-1))),angle=CCW and -angle or angle)
    
def JContact_tab(chip,structure,radius=None,ptDensity=120,bgcolor=None,**kwargs):
    def struct():
        if isinstance(structure,m.Structure):
            return structure
        else:
            return chip.structure(structure)
    if radius is None:
        try:
            radius = struct().defaults['radius']
        except KeyError:
            print('\x1b[33mradius not defined in ',chip.chipID,'!\x1b[0m')
            return
    if bgcolor is None:
        bgcolor = chip.wafer.bg()