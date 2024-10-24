import maskLib.MaskLib as m
import maskLib.microwaveLib as mw
from dxfwrite import DXFEngine as dxf


def junction_chain(chip, structure, n_junc_array=None, window=0.57, ja_length=None, gap=None, 
                   bgcolor=None, CW=True, array_sep = None, connect_w = 2,
                   finalpiece=True, Jlayer=None, Ulayer=None, **kwargs):
    def struct():
        if isinstance(structure, m.Structure):
            return structure
        elif isinstance(structure, tuple):
            #TODO FIX
            return m.Structure(chip, start = structure)
        else:
            return chip.structure(structure)
    
    if array_sep is None or array_sep < ja_length:
        array_sep = ja_length

    struct().translatePos((0, -ja_length/2))

    if n_junc_array[0] >= 1:
    
        chip.add(dxf.rectangle(struct().getPos((0, 0)), window, ja_length,
                                        rotation=struct().direction, bgcolor=bgcolor, layer=Jlayer),
                                        structure=structure, length = window)
    
        for count, n in enumerate(n_junc_array):

            chip.add(dxf.rectangle(struct().getPos((0, 0)), gap, ja_length,
                                    rotation=struct().direction, bgcolor=bgcolor, layer=Ulayer),
                                    structure=structure, length = gap)
            for i in range(n-1):
                chip.add(dxf.rectangle(struct().getPos((0, 0)), window, ja_length,
                                    rotation=struct().direction, bgcolor=bgcolor, layer=Jlayer),
                                    structure=structure, length= window )

                chip.add(dxf.rectangle(struct().getPos((0, 0)), gap, ja_length,
                                    rotation=struct().direction, bgcolor=bgcolor, layer=Ulayer),
                                    structure=structure, length= gap)
            if len(n_junc_array) >= 1:
                if CW:
                    if count % 2 == 0:
                        factor = -array_sep - ja_length
                        array_offset = -array_sep
                    else:
                        factor = 0
                        array_offset = 2 * ja_length + array_sep
                else:
                    if count % 2 == 0:
                        factor = 0
                        array_offset = 2 * ja_length + array_sep
                    else:
                        factor = -array_sep - ja_length
                        array_offset = -array_sep

                if count + 1 < len(n_junc_array):
                    connectors =  struct().cloneAlong((0, factor + (2 * ja_length + array_sep) /2 ), )
                    mw.Strip_stub_open(chip, connectors, length=2, r_out = 1, 
                                       w= 2 * ja_length + array_sep, layer=Jlayer, curve_out = True, **kwargs)
                    # chip.add(dxf.rectangle(struct().getPos((0, factor)),connect_w,
                    #                        2 * ja_length + array_sep, rotation=struct().direction,
                    #                         bgcolor=bgcolor, layer=Jlayer))
                    struct().translatePos((0, array_offset), angle=180)
                
                elif finalpiece:
                    chip.add(dxf.rectangle(struct().getPos((0, factor*ja_length)),connect_w,
                                           2 * ja_length + array_sep, rotation=struct().direction,
                                            bgcolor=bgcolor, layer=Jlayer))
                    struct().translatePos((0, array_offset), angle=180)

    chip.add(dxf.rectangle(struct().getPos((0, 0)), window, ja_length,
                                rotation=struct().direction, bgcolor=bgcolor, layer=Jlayer),
                                structure=structure, length= window )
    struct().translatePos((0, +ja_length/2))

def smallJ(chip, structure, start, j_length, Jlayer, Ulayer, gap=0.14, lead = 1, 
           vertical = False, forward = 1, **kwargs):

    x, y = start

    tmp = round(200 * (lead - j_length) / 2) / 200 # rounding to make sure it falls in 5nm grid
    
    # taper = 0.5
    # taper (0.5) + finger (1.36) + gap (0.14) = lead (2) speficiied by LL
    # taper extend over finger <2 on ech side
    if not vertical:
        #TODO FIX
        j_quad = dxf.polyline(points=[[x, y], [x+0.5, y-tmp], [x+0.5, y-tmp-j_length], [x, y-lead], [x, y]], bgcolor=chip.wafer.bg(), layer=Jlayer)
        j_quad.close()
        chip.add(j_quad)

        u_quad = dxf.polyline(points=[[x, y], [x+0.5, y-tmp], [x+0.5, y-tmp-j_length], [x, y-lead], [x, y]], bgcolor=chip.wafer.bg(), layer=Ulayer)
        u_quad.close()
        chip.add(u_quad)

        structure.translatePos((0.5, -tmp-j_length), angle=0)
        
        chip.add(dxf.rectangle(structure.getPos((0, 0)), 1.36, j_length,
                            rotation=structure.direction, bgcolor=chip.wafer.bg(), layer=Jlayer))
        chip.add(dxf.rectangle(structure.getPos((0, 0)), 1.36 + gap, j_length,
                            rotation=structure.direction, bgcolor=chip.wafer.bg(), layer=Ulayer))
        structure.translatePos((1.36 + gap, j_length/2), angle=0)

    elif vertical:

        j_quad = dxf.polyline(points=[[x,  y], [x-lead/2,  y], 
                                      [x-lead/2+tmp, y+forward *0.5], 
                                      [x-lead/2+tmp+j_length, y+ forward *0.5],
                                      [x+lead/2, y], [x, y]], bgcolor=chip.wafer.bg(), layer=Jlayer)
        j_quad.close()
        chip.add(j_quad)

        u_quad = dxf.polyline(points=[[x, y], [x-lead/2, y], 
                                      [x-lead/2+tmp, y+forward * 0.5], 
                                      [x-lead/2+tmp+j_length, y+ forward *0.5],
                                      [x+lead/2, y], [x, y]], bgcolor=chip.wafer.bg(), layer=Ulayer)
        u_quad.close()
        chip.add(u_quad)

        structure.translatePos((0.5, lead/2-tmp-j_length), angle=0)
        
        chip.add(dxf.rectangle(structure.getPos((0, 0)), 1.36, j_length,
                            rotation=structure.direction, bgcolor=chip.wafer.bg(), layer=Jlayer))
        chip.add(dxf.rectangle(structure.getPos((0, 0)), 1.36 + gap, j_length,
                            rotation=structure.direction, bgcolor=chip.wafer.bg(), layer=Ulayer))
        
        structure.translatePos((1.36 + gap, +j_length/2), angle=0)
        # base > j_length by 0.25 on each side
        mw.Strip_taper(chip, structure, length = .5, w0 = j_length + 0.5, w1 = lead, layer = Jlayer)

def bumpbond_line(chip, structure, length, row=1):
    s_bumpbond = structure.clone()
    s_bumpbond_I=s_bumpbond.clone()
    s_bond = s_bumpbond.cloneAlong((0,-(30 + (row-1)*35)/2+15))
    mw.Strip_straight(chip, s_bumpbond, length = length, w = 30 + (row-1)*35, layer = '140_IUBM')
    mw.Strip_straight(chip, s_bumpbond_I, length = length, w = 30 + (row-1)*35, layer = '40_UBM')
    if length < 30:
        n_bond = 0
    elif length >=30:
        n_bond = int((length-30) / 35) + 1
    for j in range(row):
        for i in range(n_bond):
            chip.add(dxf.circle(radius=7.5, center=s_bond.getPos((15+(i)*35, (j)*35)), 
                        bgcolor=chip.wafer.bg(), layer='145_IBUMP'))

def zipline_straight(chip, structure, length, w, bond_row= [1,1], bond_delay = 10):
    for i in range(2):
        s_bumpbond = structure.cloneAlong((bond_delay,(-1)**(i+1)*((w+30+ (bond_row[i]-1)*35)/2+10)))
        bumpbond_line(chip, s_bumpbond, length= length - bond_delay, row = bond_row[i])

    mw.Strip_straight(chip, structure, length = length, w = w, layer = '105_IM1')

def nm_zipline_straight(chip, structure, length, w, nm_delay=0):
    layerUBM = ['40_UBM', '140_IUBM']
    s_M = structure.clone()
    mw.Strip_straight(chip, structure, length = length, w = w, layer = '105_IM1')
    for i in range (2):
        s_UBM = s_M.cloneAlong((nm_delay,0))
        mw.Strip_straight(chip, s_UBM, length = length - nm_delay, w = w + 20, layer = layerUBM[i])
    mw.Strip_straight(chip, s_M, length = length, w = w, layer = '5_M1')
    return 

def nm_zipline_bend(chip, structure, radius, angle, w, CCW = True, nm_delay=10):
    layerUBM = ['40_UBM', '140_IUBM']
    s_M = structure.clone()
    mw.Strip_bend(chip, structure, radius = radius,  angle = angle, w = w, CCW = CCW, layer = '105_IM1')
    for i in range (2):
        s_UBM = s_M.cloneAlong((0,0))
        mw.Strip_bend(chip, s_UBM, radius = radius,  angle = angle, w = w + 20, CCW = CCW, layer = layerUBM[i])
    mw.Strip_bend(chip, s_M, radius = radius,  angle = angle, CCW = CCW, w = w, layer = '5_M1')
    return 

def C_shaped_cutout(chip,structure,layer):
    C_structure = structure.clone()
    mw.Strip_straight(chip, C_structure, length=2, w = 2, layer = layer)
    mw.Strip_straight(chip, C_structure, length=2, w = 6, layer = layer)
    
