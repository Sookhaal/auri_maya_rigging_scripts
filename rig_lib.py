from PySide2 import QtGui

from pymel import core as pmc
from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, is_checked, grpbox

pmc.loadPlugin("matrixNodes", qt=1)


class RigController(AuriScriptController):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.modules_with_output = QtGui.QStringListModel()
        self.outputs_model = QtGui.QStringListModel()
        self.has_updated_modules = False
        self.has_updated_outputs = False
        self.current_module = None
        AuriScriptController.__init__(self)

    def look_for_parent(self):
        if not pmc.objExists("temporary_output"):
            return
        temp_output = pmc.ls("temporary_output")[0]

        self.has_updated_modules = False
        children_list = list_children(temp_output)
        children_list.append("No_parent")
        self.modules_with_output.setStringList(children_list)
        self.model.selected_module = cbbox_set_selected(self.model.selected_module, self.view.modules_cbbox)
        self.has_updated_modules = True

        if self.model.selected_module == "No_parent":
            self.outputs_model.removeRows(0, self.outputs_model.rowCount())
            return
        self.current_module = pmc.ls(self.model.selected_module)[0]
        self.has_updated_outputs = False
        self.outputs_model.setStringList(list_children(self.current_module))
        self.model.selected_output = cbbox_set_selected(self.model.selected_output, self.view.outputs_cbbox)
        self.has_updated_outputs = True

    def on_ik_creation_switch_changed(self, state):
        self.model.ik_creation_switch = is_checked(state)

    def on_stretch_creation_switch_changed(self, state):
        self.model.stretch_creation_switch = is_checked(state)

    def on_how_many_jnts_changed(self, value):
        self.model.how_many_jnts = value

    def on_how_many_ctrls_changed(self, value):
        self.model.how_many_ctrls = value

    def on_side_cbbox_changed(self, text):
        self.model.side = text

    def on_modules_cbbox_changed(self, text):
        if self.has_updated_modules:
            self.model.selected_module = text
            self.look_for_parent()

    def on_outputs_cbbox_changed(self, text):
        if self.has_updated_outputs:
            self.model.selected_output = text


def square_arrow_curve(name):
    crv = pmc.curve(d=1, p=[(-5, 0, -5), (-2, 0, -5), (-2, 0, -7), (-3, 0, -7), (0, 0, -9), (3, 0, -7), (2, 0, -7),
                            (2, 0, -5),
                            (5, 0, -5), (5, 0, -2), (7, 0, -2), (7, 0, -3), (9, 0, 0), (7, 0, 3), (7, 0, 2), (5, 0, 2),
                            (5, 0, 5), (2, 0, 5), (2, 0, 7), (3, 0, 7), (0, 0, 9), (-3, 0, 7), (-2, 0, 7), (-2, 0, 5),
                            (-5, 0, 5), (-5, 0, 2), (-7, 0, 2), (-7, 0, 3), (-9, 0, 0), (-7, 0, -3), (-7, 0, -2),
                            (-5, 0, -2),
                            (-5, 0, -5)], n=name)
    return crv


def box_curve(name):
    crv = pmc.curve(d=1, p=[(-3, 1, 3), (-3, 1, -3), (-3, -1, -3), (-3, -1, 3), (-3, 1, 3), (3, 1, 3), (3, -1, 3),
                            (-3, -1, 3), (-3, -1, -3), (3, -1, -3), (3, 1, -3), (-3, 1, -3), (-3, -1, -3), (3, -1, -3),
                            (3, -1, 3), (3, 1, 3), (3, 1, -3)], n=name)
    return crv


def little_cube(name):
    crv = pmc.curve(d=1, p=[(-0.25, 0.25, 0.25), (-0.25, 0.25, -0.25), (-0.25, -0.25, -0.25), (-0.25, -0.25, 0.25),
                            (-0.25, 0.25, 0.25),
                            (0.25, 0.25, 0.25), (0.25, -0.25, 0.25), (-0.25, -0.25, 0.25), (-0.25, -0.25, -0.25),
                            (0.25, -0.25, -0.25),
                            (0.25, 0.25, -0.25), (-0.25, 0.25, -0.25), (-0.25, -0.25, -0.25), (0.25, -0.25, -0.25),
                            (0.25, -0.25, 0.25),
                            (0.25, 0.25, 0.25), (0.25, 0.25, -0.25)], n=name)
    return crv


def medium_cube(name):
    crv = pmc.curve(d=1, p=[(-0.75, 0.75, 0.75), (-0.75, 0.75, -0.75), (-0.75, -0.75, -0.75), (-0.75, -0.75, 0.75),
                            (-0.75, 0.75, 0.75),
                            (0.75, 0.75, 0.75), (0.75, -0.75, 0.75), (-0.75, -0.75, 0.75), (-0.75, -0.75, -0.75),
                            (0.75, -0.75, -0.75),
                            (0.75, 0.75, -0.75), (-0.75, 0.75, -0.75), (-0.75, -0.75, -0.75), (0.75, -0.75, -0.75),
                            (0.75, -0.75, 0.75),
                            (0.75, 0.75, 0.75), (0.75, 0.75, -0.75)], n=name)
    return crv


def jnt_shape_curve(name):
    crv = pmc.curve(d=1, p=[(0, 1.005374, 0), (0.174398, 0.989251, 0), (0.343339, 0.943378, 0), (0.502058, 0.869564, 0),
                            (0.646013, 0.769872, 0), (0.769868, 0.64603, 0), (0.869533, 0.502059, 0),
                            (0.943416, 0.343375, 0), (0.989245, 0.174409, 0), (1.00521, 0, -5.53792e-006),
                            (0.989248, -0.174399, 0), (0.943422, -0.343364, 0), (0.869538, -0.50205, 0),
                            (0.769867, -0.646015, 0), (0.646022, -0.769867, 0), (0.502078, -0.869574, 0),
                            (0.343351, -0.943378, 0), (0.174399, -0.989209, 0), (0, -1.005305, 0),
                            (-0.174399, -0.989209, 0), (-0.343351, -0.943378, 0), (-0.502078, -0.869574, 0),
                            (-0.646022, -0.769867, 0), (-0.769867, -0.646015, 0), (-0.869538, -0.50205, 0),
                            (-0.943422, -0.343364, 0), (-0.989248, -0.174399, 0), (-1.00521, 0, -5.53792e-006),
                            (-0.989245, 0.174409, 0), (-0.943416, 0.343375, 0), (-0.869533, 0.502059, 0),
                            (-0.769868, 0.64603, 0), (-0.646013, 0.769872, 0), (-0.502058, 0.869564, 0),
                            (-0.343339, 0.943378, 0), (-0.174398, 0.989251, 0), (0, 1.005374, 0),
                            (0, 0.989251, 0.174398), (0, 0.943378, 0.343339), (0, 0.869564, 0.502058),
                            (0, 0.769872, 0.646013), (0, 0.64603, 0.769868), (0, 0.502059, 0.869533),
                            (0, 0.343375, 0.943416), (0, 0.174409, 0.989245), (0, 5.53792e-006, 1.00521),
                            (0, -0.174399, 0.989248), (0, -0.343364, 0.943422), (0, -0.50205, 0.869538),
                            (0, -0.646015, 0.769867), (0, -0.769867, 0.646022), (0, -0.869574, 0.502078),
                            (0, -0.943378, 0.343351), (0, -0.989209, 0.174399), (0, -1.005305, 0),
                            (0, -0.989209, -0.174399), (0, -0.943378, -0.343351), (0, -0.869574, -0.502078),
                            (0, -0.769867, -0.646022), (0, -0.646015, -0.769867), (0, -0.50205, -0.869538),
                            (0, -0.343364, -0.943422), (0, -0.174399, -0.989248), (0, 5.53792e-006, -1.00521),
                            (0.174398, 0, -0.989251), (0.343339, 0, -0.943378), (0.502058, 0, -0.869564),
                            (0.646013, 0, -0.769872), (0.769868, 0, -0.64603), (0.869533, 0, -0.502059),
                            (0.943416, 0, -0.343375), (0.989245, 0, -0.174409), (1.00521, 0, -5.53792e-006),
                            (0.989248, 0, 0.174399), (0.943422, 0, 0.343364), (0.869538, 0, 0.50205),
                            (0.769867, 0, 0.646015), (0.646022, 0, 0.769867), (0.502078, 0, 0.869574),
                            (0.343351, 0, 0.943378), (0.174399, 0, 0.989209), (0, 5.53792e-006, 1.00521),
                            (-0.174399, 0, 0.989209), (-0.343351, 0, 0.943378), (-0.502078, 0, 0.869574),
                            (-0.646022, 0, 0.769867), (-0.769867, 0, 0.646015), (-0.869538, 0, 0.50205),
                            (-0.943422, 0, 0.343364), (-0.989248, 0, 0.174399), (-1.00521, 0, -5.53792e-006),
                            (-0.989245, 0, -0.174409), (-0.943416, 0, -0.343375), (-0.869533, 0, -0.502059),
                            (-0.769868, 0, -0.64603), (-0.646013, 0, -0.769872), (-0.502058, 0, -0.869564),
                            (-0.343339, 0, -0.943378), (-0.174398, 0, -0.989251), (0, 5.53792e-006, -1.00521),
                            (0, 0.174409, -0.989245), (0, 0.343375, -0.943416), (0, 0.502059, -0.869533),
                            (0, 0.64603, -0.769868), (0, 0.769872, -0.646013), (0, 0.869564, -0.502058),
                            (0, 0.943378, -0.343339), (0, 0.989251, -0.174398), (0, 1.005374, 0)], n=name)
    return crv


def matrix_constraint(driver, driven, srt="srt"):
    """ Constraint one node to another using their worldMatrix attributes
        if doesn't work, check if plug-in "matrixNodes" is loaded
    """

    # define/create nodes
    mmlt = pmc.createNode("multMatrix", name=driven + "_multMatrix")
    mdcp = pmc.createNode("decomposeMatrix", name=driven + "_decomposeMatrix")

    if driver.type() == "choice":
        driver.output >> mmlt.matrixIn[0]
    else:
        driver.worldMatrix[0] >> mmlt.matrixIn[0]

    driven.parentInverseMatrix[0] >> mmlt.matrixIn[1]
    mmlt.matrixSum >> mdcp.inputMatrix

    for attr in [x + y for x in srt.lower() for y in "xyz"]:
        mdcp.attr("o" + attr) >> driven.attr(attr)

    return mmlt, mdcp


def change_shape_color(selection, color):
    """ 2=dark_grey, 3=light_grey, 6=blue, 9=rose, 13=red, 14=green, 17=yellow """
    if isinstance(selection, list):
        for obj in selection:
            shape = obj.getShape()
            pmc.setAttr(shape + ".overrideEnabled", 1)
            pmc.setAttr(shape + ".overrideColor", color)
    else:
        shape = selection.getShape()
        pmc.setAttr(shape + ".overrideEnabled", 1)
        pmc.setAttr(shape + ".overrideColor", color)


def exists_check(objects):
    if isinstance(objects, (str, unicode)):
        if not pmc.objExists(objects):
            return False
        return True
    elif type(objects) == list:
        for obj in objects:
            if not pmc.objExists(obj):
                return False
        return True
    else:
        print("Wrong argument given to exists_check fonction")


def list_children(group):
    return [obj.nodeName() for obj in pmc.listRelatives(group, children=1)]


def cbbox_set_selected(selected, cbbox):
    if selected is not None and cbbox.findText(selected) != -1:
        cbbox.setCurrentText(selected)
    else:
        cbbox.setCurrentIndex(0)
        selected = cbbox.currentText()
    return selected


def create_curve_guide(d, number_of_points, name, hauteur_curve=10):
    crv = pmc.curve(d=1, p=[(0, 0, 0), (hauteur_curve, 0, 0)], k=[0, 1])
    crv.setAttr("rotate", (-90, 0, 90))
    crv_rebuilded = pmc.rebuildCurve(crv, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0, s=(number_of_points - 1),
                                     d=d, ch=0, replaceOriginal=1)[0]
    crv_rebuilded.rename(name)
    return crv_rebuilded


def create_jnts_from_cv_list_and_return_jnts_list(vertex_list, guide, module_name):
    pmc.select(d=1)
    created_jnts_list = []
    for i, vertex in enumerate(vertex_list):
        if i == 0:
            jnt = pmc.joint(p=(pmc.xform(vertex, q=1, ws=1, translation=1)),
                            o=(pmc.xform(guide, q=1, ws=1, rotation=1)),
                            n="{0}_{1}_JNT".format(module_name, i), rad=0.5)
        else:
            jnt = pmc.joint(p=(pmc.xform(vertex, q=1, ws=1, translation=1)),
                            n="{0}_{1}_JNT".format(module_name, i), rad=0.5)
        created_jnts_list.append(jnt)
    created_jnts_list[-1].rename("{0}_end_JNT".format(module_name))
    return created_jnts_list


def change_jnt_chain_suffix(jnts_chain, new_suffix):
    for jnt in jnts_chain:
        if jnt != jnts_chain[-1]:
            jnt_name = jnt.name().rsplit("|")[-1]
            split_name = jnt_name.rsplit("_")
            split_name.pop(-1)
            new_suffix_list = [new_suffix]
            new_name = "_".join(split_name + new_suffix_list)
            jnt.rename(new_name)


