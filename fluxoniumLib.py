import maskLib.MaskLib as m
import maskLib.microwaveLib as mw
from dxfwrite import DXFEngine as dxf


def junction_chain(chip, structure, n_junc_array=None, window=0.57, ja_length=None, gap=None, 
                   bgcolor=None, CW=True, array_sep = None, finalpiece=True, Jlayer=None, Ulayer=None, **kwargs):
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

                    chip.add(dxf.rectangle(struct().getPos((0, factor)), window, 
                                           2 * ja_length + array_sep, rotation=struct().direction,
                                            bgcolor=bgcolor, layer=Jlayer))
                    struct().translatePos((0, array_offset), angle=180)
                
                elif finalpiece:
                    chip.add(dxf.rectangle(struct().getPos((0, factor*ja_length)), window, 
                                           2 * ja_length + array_sep, rotation=struct().direction,
                                            bgcolor=bgcolor, layer=Jlayer))
                    struct().translatePos((0, array_offset), angle=180)

    chip.add(dxf.rectangle(struct().getPos((0, 0)), window, ja_length,
                                rotation=struct().direction, bgcolor=bgcolor, layer=Jlayer),
                                structure=structure, length= window )
    struct().translatePos((0, +ja_length/2))

def smallJ(chip, structure, start, j_length, Jlayer, Ulayer, gap=0.14, lead = 1, vertical = False, **kwargs):

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

        j_quad = dxf.polyline(points=[[x, y], [x-lead/2, y], 
                                      [x-lead/2+tmp, y+0.5], [x-lead/2+tmp+j_length, y+0.5],
                                      [x+lead/2, y], [x, y]], bgcolor=chip.wafer.bg(), layer=Jlayer)
        j_quad.close()
        chip.add(j_quad)

        u_quad = dxf.polyline(points=[[x, y], [x-lead/2, y], 
                                      [x-lead/2+tmp, y+0.5], [x-lead/2+tmp+j_length, y+0.5],
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

