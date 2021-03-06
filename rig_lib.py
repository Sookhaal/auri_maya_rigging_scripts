from auri.vendor.Qt import QtCore

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, is_checked, grpbox

pmc.loadPlugin("matrixNodes", qt=1)


class RigController(AuriScriptController):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.modules_with_output = QtCore.QStringListModel()
        self.outputs_model = QtCore.QStringListModel()
        self.modules_with_spaces = QtCore.QStringListModel()
        self.spaces_model = QtCore.QStringListModel()
        self.has_updated_modules = False
        # self.current_module = None
        self.jnt_input_grp = None
        self.ctrl_input_grp = None
        self.parts_grp = None
        AuriScriptController.__init__(self)

    def look_for_parent(self, grp="temporary_outputs", l_cbbox_stringlist=None, l_cbbox_selection=None, l_cbbox=None,
                        r_cbbox_stringlist=None, r_cbbox_selection=None, r_cbbox=None):
        if not pmc.objExists(grp):
            return
        if l_cbbox is None:
            l_cbbox = self.view.modules_cbbox
        if l_cbbox_stringlist is None:
            l_cbbox_stringlist = self.modules_with_output
        if l_cbbox_selection is None:
            l_cbbox_selection = self.model.selected_module
        if r_cbbox is None:
            r_cbbox = self.view.outputs_cbbox
        if r_cbbox_stringlist is None:
            r_cbbox_stringlist = self.outputs_model
        if r_cbbox_selection is None:
            r_cbbox_selection = self.model.selected_output

        temp_output = pmc.ls(grp)[0]

        self.has_updated_modules = False
        children_list = list_children(temp_output)
        children_list.append("No_parent")
        l_cbbox_stringlist.setStringList(children_list)
        l_cbbox_selection = cbbox_set_selected(l_cbbox_selection, l_cbbox)
        self.has_updated_modules = True

        if l_cbbox_selection == "No_parent":
            r_cbbox_stringlist.removeRows(0, r_cbbox_stringlist.rowCount())
            return
        current_module = pmc.ls("{0}|{1}".format(temp_output, l_cbbox_selection))[0]
        r_cbbox_stringlist.setStringList(list_children(current_module))
        r_cbbox_selection = cbbox_set_selected(r_cbbox_selection, r_cbbox)

    def look_for_spaces(self):
        self.look_for_parent(l_cbbox_stringlist=self.modules_with_spaces,
                             l_cbbox_selection=self.view.selected_space_module,
                             l_cbbox=self.view.space_modules_cbbox, r_cbbox_stringlist=self.spaces_model,
                             r_cbbox_selection=self.view.selected_space, r_cbbox=self.view.spaces_cbbox)

    def add_space_to_list(self):
        if self.view.selected_space_module != "No_parent":
            item = "{0}_{1}".format(self.view.selected_space_module, self.view.selected_space)
            self.model.space_list.append(item)
            self.view.space_list.setStringList(self.model.space_list)

    def remove_space_from_list(self):
        indexes = self.view.space_list_view.selectedIndexes()
        indexes_to_del = []
        for index in indexes:
            # item = index.data()
            # self.model.space_list.remove(item)
            space_index = index.row()
            indexes_to_del.append(space_index)

        indexes_to_del_set = set(indexes_to_del)
        self.model.space_list = [self.model.space_list[i] for i in xrange(len(self.model.space_list)) if i not in indexes_to_del_set]

        self.view.space_list.setStringList(self.model.space_list)

    def on_ik_creation_switch_changed(self, state):
        self.model.ik_creation_switch = is_checked(state)

    def on_stretch_creation_switch_changed(self, state):
        self.model.stretch_creation_switch = is_checked(state)

    def on_clavicle_creation_switch_changed(self, state):
        self.model.clavicle_creation_switch = is_checked(state)

    def on_deform_chain_creation_switch_changed(self, state):
        self.model.deform_chain_creation_switch = is_checked(state)
        if state == 0:
            self.view.how_many_jnts.setEnabled(False)
        else:
            self.view.how_many_jnts.setEnabled(True)

    def on_how_many_jnts_changed(self, value):
        self.model.how_many_jnts = value

    def on_how_many_ctrls_changed(self, value):
        self.model.how_many_ctrls = value

    def on_how_many_levels_changed(self, value):
        self.model.how_many_levels = value

    def on_side_cbbox_changed(self, text):
        self.model.side = text

    def on_swimrotation_cbbox_changed(self, text):
        self.model.swimrotation = text

    def on_raz_ik_ctrls_changed(self, state):
        self.model.raz_ik_ctrls = is_checked(state)

    def on_raz_fk_ctrls_changed(self, state):
        self.model.raz_fk_ctrls = is_checked(state)

    def on_fk_ik_type_changed(self, text):
        self.model.fk_ik_type = text

    def on_modules_cbbox_changed(self, text):
        self.model.selected_module = text
        if self.has_updated_modules:
            self.look_for_parent()

    def on_outputs_cbbox_changed(self, text):
        self.model.selected_output = text

    def on_space_modules_cbbox_changed(self, text):
        self.view.selected_space_module = text
        if self.has_updated_modules:
            self.look_for_parent(l_cbbox_stringlist=self.modules_with_spaces,
                                 l_cbbox_selection=self.view.selected_space_module,
                                 l_cbbox=self.view.space_modules_cbbox, r_cbbox_stringlist=self.spaces_model,
                                 r_cbbox_selection=self.view.selected_space, r_cbbox=self.view.spaces_cbbox)

    def on_spaces_cbbox_changed(self, text):
        self.view.selected_space = text

    def set_mesh_to_follow(self):
        self.model.mesh_to_follow = str(pmc.ls(sl=1)[0])
        self.view.refresh_view()

    def create_temporary_outputs(self, outputs_names, grp_name="temporary_outputs"):
        if not pmc.objExists(grp_name):
            pmc.group(em=1, n=grp_name)
        temp_output_grp = pmc.ls(grp_name)[0]

        if not pmc.objExists("{0}|{1}".format(grp_name, self.model.module_name)):
            pmc.group(em=1, n="{0}".format(self.model.module_name), p=temp_output_grp)
        module_grp = pmc.ls("{0}|{1}".format(grp_name, self.model.module_name))[0]

        for output in outputs_names:
            if not pmc.objExists("{0}|{1}|{2}".format(grp_name, self.model.module_name, output)):
                pmc.group(em=1, n="{0}".format(output), p=module_grp)

    # def create_out_objects(self, outputs_objects_names):
    #     if not pmc.objExists("temporary_out_objects"):
    #         pmc.group(em=1, n="temporary_out_objects")
    #     temp_output_grp = pmc.ls("temporary_out_objects")[0]
    #
    #     if not pmc.objExists("temporary_out_objects|{0}".format(self.model.module_name)):
    #         pmc.group(em=1, n="{0}".format(self.model.module_name), p=temp_output_grp)
    #     module_grp = pmc.ls("{0}".format(self.model.module_name))[0]
    #
    #     for obj in outputs_objects_names:
    #         if not pmc.objExists("temporary_out_objects|{0}|{1}".format(self.model.module_name, obj)):
    #             pmc.group(em=1, n="{0}".format(obj), p=module_grp)

    def guide_check(self, guides_names):
        if not pmc.objExists("guide_GRP"):
            return False
        if not pmc.objExists("guide_GRP|{0}_guides".format(self.model.module_name)):
            return False
        if isinstance(guides_names, (str, unicode)):
            # if not pmc.objExists("guide_GRP|{0}_guides|{1}".format(self.model.module_name, guides_names)):
            try:
                pmc.ls(regex="guide_GRP\|{0}_guides\|.*{1}$".format(self.model.module_name, guides_names))[0]
            except:
                return False
        elif type(guides_names) == list:
            for guide in guides_names:
                if isinstance(guide, (str, unicode)):
                    # if not pmc.objExists("guide_GRP|{0}_guides|{1}".format(self.model.module_name, guide)):
                    try:
                        pmc.ls(regex="guide_GRP\|{0}_guides\|.*{1}$".format(self.model.module_name, guide))[0]
                    except:
                        return False
                elif type(guide) == list:
                    for obj in guide:
                        # if not pmc.objExists("guide_GRP|{0}_guides|{1}".format(self.model.module_name, obj)):
                        try:
                            pmc.ls(regex="guide_GRP\|{0}_guides\|.*{1}$".format(self.model.module_name, obj))[0]
                        except:
                            return False
                else:
                    print("Wrong argument given to guide_check fonction")
        else:
            print("Wrong argument given to guide_check fonction")
        return True

    def group_guides(self, guides):
        if not pmc.objExists("{0}_guides".format(self.model.module_name)):
            pmc.group(em=1, n="{0}_guides".format(self.model.module_name))
        else:
            pmc.delete("{0}_guides".format(self.model.module_name))
            pmc.group(em=1, n="{0}_guides".format(self.model.module_name))
        guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]

        if type(guides) == list:
            for guide in guides:
                if type(guide) == list:
                    for obj in guide:
                        pmc.parent(obj, guides_grp, r=0)
                else:
                    pmc.parent(guide, guides_grp, r=0)
        else:
            pmc.parent(guides, guides_grp, r=0)

        if not pmc.objExists("guide_GRP"):
            pmc.group(em=1, n="guide_GRP")
        pmc.parent(guides_grp, "guide_GRP")
        return guides_grp

    def delete_existing_objects(self):
        if exists_check("{0}_jnt_INPUT".format(self.model.module_name)):
            pmc.delete("{0}_jnt_INPUT".format(self.model.module_name))
        if exists_check("{0}_ctrl_INPUT".format(self.model.module_name)):
            pmc.delete("{0}_ctrl_INPUT".format(self.model.module_name))
        if exists_check("{0}_parts_INPUT".format(self.model.module_name)):
            pmc.delete("{0}_parts_INPUT".format(self.model.module_name))

    def connect_to_parent(self):
        check_list = ["CTRL_GRP", "JNT_GRP", "PARTS_GRP"]
        if not exists_check(check_list):
            print("No necessary groups created for module {0}".format(self.model.module_name))
            return

        self.jnt_input_grp = pmc.group(em=1, n="{0}_jnt_INPUT".format(self.model.module_name))
        self.ctrl_input_grp = pmc.group(em=1, n="{0}_ctrl_INPUT".format(self.model.module_name))
        self.parts_grp = pmc.group(em=1, n="{0}_parts_INPUT".format(self.model.module_name))

        if self.model.selected_module != "No_parent" and self.model.selected_module != "{0}".format(
                self.model.module_name):
            parent_name = "{0}_{1}".format(self.model.selected_module, self.model.selected_output)
            parent_node = pmc.ls(parent_name)[0]
            matrix_constraint(parent_node, self.ctrl_input_grp, srt="trs")
            matrix_constraint(parent_node, self.jnt_input_grp, srt="trs")
        else:
            print("No parent for module {0}".format(self.model.module_name))

        pmc.parent(self.jnt_input_grp, "JNT_GRP", r=1)
        pmc.parent(self.parts_grp, "PARTS_GRP", r=1)

        local_ctrl_list = pmc.ls(regex=".*_local_CTRL$")
        if len(local_ctrl_list) > 0:
            local_ctrl = local_ctrl_list[0]
            pmc.parent(self.ctrl_input_grp, local_ctrl, r=1)
        else:
            pmc.parent(self.ctrl_input_grp, "CTRL_GRP", r=1)

    def connect_ik_spline_stretch(self, ik_spline, created_jnts, measure_type="average"):
        if measure_type == "average":
            crv_info = pmc.createNode("curveInfo", n="{0}_CURVEINFO".format(self.model.module_name))
            global_stretch = pmc.createNode("multDoubleLinear", n="{0}_global_stretch_MDL".format(self.model.module_name))
            neck_stretch_div = pmc.createNode("multiplyDivide", n="{0}_stretch_MDIV".format(self.model.module_name))
            neck_stretch_mult = pmc.createNode("multDoubleLinear", n="{0}_stretch_MDL".format(self.model.module_name))
            self.jnt_input_grp.addAttr("baseArcLength", attributeType="float", defaultValue=0, hidden=0, keyable=1)
            self.jnt_input_grp.addAttr("baseTranslateY", attributeType="float", defaultValue=0, hidden=0, keyable=1)
            crv_shape = ik_spline.getShape()
            global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]

            crv_shape.worldSpace[0] >> crv_info.inputCurve
            base_arc_length = crv_info.getAttr("arcLength")
            self.jnt_input_grp.setAttr("baseArcLength", base_arc_length)
            base_translate_y = created_jnts[1].getAttr("translateY")
            self.jnt_input_grp.setAttr("baseTranslateY", base_translate_y)
            global_scale.output >> global_stretch.input1
            self.jnt_input_grp.baseArcLength >> global_stretch.input2
            crv_info.arcLength >> neck_stretch_div.input1X
            global_stretch.output >> neck_stretch_div.input2X
            neck_stretch_div.setAttr("operation", 2)
            neck_stretch_div.outputX >> neck_stretch_mult.input1
            self.jnt_input_grp.baseTranslateY >> neck_stretch_mult.input2

            for jnt in created_jnts:
                if not jnt == created_jnts[0]:
                    neck_stretch_mult.output >> jnt.translateY
        else:
            nearest_point = pmc.createNode("nearestPointOnCurve", n="temp_nearest_point_on_curve")
            pos_loc = pmc.spaceLocator(p=(0, 0, 0), n="temp_loc_for_ik_stretch")
            ik_spline.getShape().worldSpace[0] >> nearest_point.inputCurve
            pos_loc.getShape().worldPosition[0] >> nearest_point.inPosition

            jnt_locs = []
            loc_group = pmc.group(em=1, n="{0}_stretch_locs_GRP".format(ik_spline))

            for i, jnt in enumerate(created_jnts):
                pmc.xform(pos_loc, ws=1, matrix=(pmc.xform(jnt, q=1, ws=1, matrix=1)))

                jnt_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_jnt_{1}_LOC".format(ik_spline, i))
                # point_on_curve = pmc.createNode("pointOnCurveInfo", n="{0}_pos_POCI".format(jnt_loc))
                point_on_curve = pmc.createNode("motionPath", n="{0}_pos_POCI".format(jnt_loc))
                point_on_curve.setAttr("fractionMode", 1)
                # ik_spline.getShape().worldSpace[0] >> point_on_curve.inputCurve
                ik_spline.getShape().worldSpace[0] >> point_on_curve.geometryPath
                pmc.refresh()

                # point_on_curve.setAttr("parameter", nearest_point.getAttr("parameter"))
                point_on_curve.setAttr("uValue", nearest_point.getAttr("parameter"))
                # point_on_curve.position >> jnt_loc.translate
                point_on_curve.allCoordinates >> jnt_loc.translate

                jnt_locs.append(jnt_loc)
                pmc.parent(jnt_loc, loc_group)

                pmc.refresh()

                if i > 0:
                    distance = pmc.createNode("distanceBetween",
                                              n="{0}_jnt{1}_to_jnt{2}_distance_DSTBTN".format(self.model.module_name, i-1, i))
                    jnt_locs[i-1].getShape().worldPosition >> distance.point1
                    jnt_locs[i].getShape().worldPosition >> distance.point2
                    jnt.addAttr("baseDistance", attributeType="float", defaultValue=0, hidden=0, keyable=1)
                    jnt.addAttr("baseTranslateY", attributeType="float", defaultValue=0, hidden=0, keyable=1)

                    global_stretch = pmc.createNode("multDoubleLinear",
                                                    n="{0}_global_stretch_MDL".format(self.model.module_name))
                    jnt_stretch_div = pmc.createNode("multiplyDivide", n="{0}_stretch_MDIV".format(self.model.module_name))
                    jnt_stretch_mult = pmc.createNode("multDoubleLinear", n="{0}_stretch_MDL".format(self.model.module_name))
                    global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]

                    jnt.setAttr("baseDistance", distance.getAttr("distance"))
                    jnt.setAttr("baseTranslateY", jnt.getAttr("translateY"))
                    global_scale.output >> global_stretch.input1
                    jnt.baseDistance >> global_stretch.input2
                    distance.distance >> jnt_stretch_div.input1X
                    global_stretch.output >> jnt_stretch_div.input2X
                    jnt_stretch_div.setAttr("operation", 2)
                    jnt_stretch_div.outputX >> jnt_stretch_mult.input1
                    jnt.baseTranslateY >> jnt_stretch_mult.input2
                    jnt_stretch_mult.output >> jnt.translateY

            pmc.parent(loc_group, self.parts_grp)
            loc_group.setAttr("visibility", 0)

            pmc.delete(nearest_point)
            pmc.delete(pos_loc)

    def connect_z_ik_spline_stretch(self, ik_spline, created_jnts, measure_type="average"):
        if measure_type == "average":
            crv_info = pmc.createNode("curveInfo", n="{0}_CURVEINFO".format(self.model.module_name))
            global_stretch = pmc.createNode("multDoubleLinear",
                                            n="{0}_global_stretch_MDL".format(self.model.module_name))
            neck_stretch_div = pmc.createNode("multiplyDivide", n="{0}_stretch_MDIV".format(self.model.module_name))
            neck_stretch_mult = pmc.createNode("multDoubleLinear", n="{0}_stretch_MDL".format(self.model.module_name))
            self.jnt_input_grp.addAttr("baseArcLength", attributeType="float", defaultValue=0, hidden=0, keyable=1)
            self.jnt_input_grp.addAttr("baseTranslateZ", attributeType="float", defaultValue=0, hidden=0, keyable=1)
            crv_shape = ik_spline.getShape()
            global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]

            crv_shape.worldSpace[0] >> crv_info.inputCurve
            base_arc_length = crv_info.getAttr("arcLength")
            self.jnt_input_grp.setAttr("baseArcLength", base_arc_length)
            base_translate_Z = created_jnts[1].getAttr("translateZ")
            self.jnt_input_grp.setAttr("baseTranslateZ", base_translate_Z)
            global_scale.output >> global_stretch.input1
            self.jnt_input_grp.baseArcLength >> global_stretch.input2
            crv_info.arcLength >> neck_stretch_div.input1X
            global_stretch.output >> neck_stretch_div.input2X
            neck_stretch_div.setAttr("operation", 2)
            neck_stretch_div.outputX >> neck_stretch_mult.input1
            self.jnt_input_grp.baseTranslateZ >> neck_stretch_mult.input2

            for jnt in created_jnts:
                if not jnt == created_jnts[0]:
                    neck_stretch_mult.output >> jnt.translateZ
        else:
            nearest_point = pmc.createNode("nearestPointOnCurve", n="temp_nearest_point_on_curve")
            pos_loc = pmc.spaceLocator(p=(0, 0, 0), n="temp_loc_for_ik_stretch")
            ik_spline.getShape().worldSpace[0] >> nearest_point.inputCurve
            pos_loc.getShape().worldPosition[0] >> nearest_point.inPosition

            jnt_locs = []
            loc_group = pmc.group(em=1, n="{0}_stretch_locs_GRP".format(ik_spline))

            for i, jnt in enumerate(created_jnts):
                pmc.xform(pos_loc, ws=1, matrix=(pmc.xform(jnt, q=1, ws=1, matrix=1)))

                jnt_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_jnt_{1}_LOC".format(ik_spline, i))
                # point_on_curve = pmc.createNode("pointOnCurveInfo", n="{0}_pos_POCI".format(jnt_loc))
                point_on_curve = pmc.createNode("motionPath", n="{0}_pos_POCI".format(jnt_loc))
                point_on_curve.setAttr("fractionMode", 1)
                # ik_spline.getShape().worldSpace[0] >> point_on_curve.inputCurve
                ik_spline.getShape().worldSpace[0] >> point_on_curve.geometryPath
                pmc.refresh()

                # point_on_curve.setAttr("parameter", nearest_point.getAttr("parameter"))
                point_on_curve.setAttr("uValue", nearest_point.getAttr("parameter"))
                # point_on_curve.position >> jnt_loc.translate
                point_on_curve.allCoordinates >> jnt_loc.translate

                jnt_locs.append(jnt_loc)
                pmc.parent(jnt_loc, loc_group)

                pmc.refresh()

                if i > 0:
                    distance = pmc.createNode("distanceBetween",
                                              n="{0}_jnt{1}_to_jnt{2}_distance_DSTBTN".format(self.model.module_name,
                                                                                              i - 1, i))
                    jnt_locs[i - 1].getShape().worldPosition >> distance.point1
                    jnt_locs[i].getShape().worldPosition >> distance.point2
                    jnt.addAttr("baseDistance", attributeType="float", defaultValue=0, hidden=0, keyable=1)
                    jnt.addAttr("baseTranslateZ", attributeType="float", defaultValue=0, hidden=0, keyable=1)

                    global_stretch = pmc.createNode("multDoubleLinear",
                                                    n="{0}_global_stretch_MDL".format(self.model.module_name))
                    jnt_stretch_div = pmc.createNode("multiplyDivide",
                                                     n="{0}_stretch_MDIV".format(self.model.module_name))
                    jnt_stretch_mult = pmc.createNode("multDoubleLinear",
                                                      n="{0}_stretch_MDL".format(self.model.module_name))
                    global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]

                    jnt.setAttr("baseDistance", distance.getAttr("distance"))
                    jnt.setAttr("baseTranslateZ", jnt.getAttr("translateZ"))
                    global_scale.output >> global_stretch.input1
                    jnt.baseDistance >> global_stretch.input2
                    distance.distance >> jnt_stretch_div.input1X
                    global_stretch.output >> jnt_stretch_div.input2X
                    jnt_stretch_div.setAttr("operation", 2)
                    jnt_stretch_div.outputX >> jnt_stretch_mult.input1
                    jnt.baseTranslateZ >> jnt_stretch_mult.input2
                    jnt_stretch_mult.output >> jnt.translateZ

            pmc.parent(loc_group, self.parts_grp)
            loc_group.setAttr("visibility", 0)

            pmc.delete(nearest_point)
            pmc.delete(pos_loc)

    def connect_fk_stretch(self, created_fk_jnts, created_fk_ctrls):
        for i, jnt in enumerate(created_fk_jnts):
            if i != 0:
                jnt.addAttr("baseTranslateY", attributeType="float",
                            defaultValue=pmc.xform(jnt, q=1, translation=1)[1], hidden=0, keyable=0)
                jnt.setAttr("baseTranslateY", lock=1, channelBox=0)
                created_fk_ctrls[i-1].addAttr("stretch", attributeType="float", defaultValue=1, hidden=0, keyable=1,
                                              hasMinValue=1, minValue=0)
                arm_mult = pmc.createNode("multDoubleLinear", n="{0}_fk_stretch_{1}_MDL".format(self.model.module_name,
                                                                                                i))
                created_fk_ctrls[i-1].stretch >> arm_mult.input1
                jnt.baseTranslateY >> arm_mult.input2
                arm_mult.output >> jnt.translateY
                arm_mult.output >> created_fk_ctrls[i].translateY

    def connect_ik_stretch(self, created_ik_jnts, created_ik_ctrls, side_coef, start_parent, end_parent, ik_ctrl_object_to_snap_to):
        jnt_stretch_mult_list = []
        for i, jnt in enumerate(created_ik_jnts):
            if i != 0:
                jnt.addAttr("baseTranslateY", attributeType="float",
                            defaultValue=(pmc.xform(jnt, q=1, translation=1)[1]), hidden=0, keyable=0)
                jnt.setAttr("baseTranslateY", lock=1, channelBox=0)
                jnt_stretch_mult = pmc.createNode("multDoubleLinear",
                                                  n="{0}_ik_stretch_mult_{1}_MDL".format(self.model.module_name, i))
                jnt_stretch_mult_list.append(jnt_stretch_mult)

        created_ik_ctrls[0].setAttr("translate", (0, 0, 0))
        created_ik_ctrls[0].setAttr("rotate", (0, 0, 0))
        start_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_start_LOC".format(self.model.module_name))
        end_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_end_LOC".format(self.model.module_name))
        pmc.parent(start_loc, start_parent, r=1)
        pmc.parent(end_loc, end_parent, r=1)
        start_loc_shape = start_loc.getShape()
        end_loc_shape = end_loc.getShape()
        length_measure = pmc.createNode("distanceDimShape", n="{0}_ik_length_measure_DDMShape".format(self.model.module_name))
        measure_transform = length_measure.getParent()
        measure_transform.rename("{0}_ik_length_measure_DDM".format(self.model.module_name))
        pmc.parent(measure_transform, self.parts_grp, r=0)
        ik_global_scale = pmc.createNode("multiplyDivide", n="{0}_ik_global_scale_MDV".format(self.model.module_name))
        ik_stretch_value = pmc.createNode("multiplyDivide", n="{0}_ik_stretch_value_MDV".format(self.model.module_name))
        stretch_condition = pmc.createNode("condition", n="{0}_ik_stretch_CONDITION".format(self.model.module_name))
        global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]

        start_loc_shape.worldPosition[0] >> length_measure.startPoint
        end_loc_shape.worldPosition[0] >> length_measure.endPoint
        ik_global_scale.setAttr("operation", 2)
        length_measure.distance >> ik_global_scale.input1X
        global_scale.output >> ik_global_scale.input2X
        ik_stretch_value.setAttr("operation", 2)
        ik_stretch_value.setAttr("input2X", length_measure.getAttr("distance"))
        ik_global_scale.outputX >> ik_stretch_value.input1X
        stretch_condition.setAttr("operation", 4)
        stretch_condition.setAttr("secondTerm", length_measure.getAttr("distance"))
        stretch_condition.setAttr("colorIfTrueR", 1)
        ik_global_scale.outputX >> stretch_condition.firstTerm
        ik_stretch_value.outputX >> stretch_condition.colorIfFalseR
        for i, jnt in enumerate(created_ik_jnts):
            if i != 0:
                stretch_condition.outColorR >> jnt_stretch_mult_list[i-1].input1
                jnt.baseTranslateY >> jnt_stretch_mult_list[i-1].input2
                jnt_stretch_mult_list[i - 1].output >> jnt.translateY

        start_loc_shape.setAttr("visibility", 0)
        end_loc_shape.setAttr("visibility", 0)

        pmc.xform(created_ik_ctrls[0], ws=1, translation=(pmc.xform(ik_ctrl_object_to_snap_to, q=1, ws=1, translation=1)))
        pmc.xform(created_ik_ctrls[0], ws=1, rotation=(pmc.xform(ik_ctrl_object_to_snap_to, q=1, ws=1, rotation=1)))

    def connect_one_chain_fk_ik_stretch(self, fk_ctrls, ik_ctrl, option_ctrl, skn_jnts, name=None, finger=False):
        if name is None:
            name = self.model.module_name

        ik_ctrl_translate = ik_ctrl.getAttr("translate")
        ik_ctrl_rotate = ik_ctrl.getAttr("rotate")
        ik_ctrl.setAttr("translate", (0, 0, 0))
        ik_ctrl.setAttr("rotate", (0, 0, 0))

        start_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_start_LOC".format(name))
        end_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_end_LOC".format(name))
        if finger:
            pmc.parent(start_loc, fk_ctrls[0], r=1)
            pmc.parent(start_loc, fk_ctrls[0].getParent(), r=0)
        else:
            pmc.parent(start_loc, fk_ctrls[0].getParent(), r=1)
        pmc.parent(end_loc, ik_ctrl, r=1)
        start_loc.setAttr("visibility", 0)
        end_loc.setAttr("visibility", 0)

        length_measure = pmc.createNode("distanceDimShape",
                                        n="{0}_ik_length_measure_DDMShape".format(name))
        length_measure.getParent().rename("{0}_ik_length_measure_DDM".format(name))
        pmc.parent(length_measure.getParent(), self.parts_grp, r=0)

        ik_global_scale = pmc.createNode("multiplyDivide", n="{0}_ik_global_scale_MDV".format(name))
        ik_stretch_value = pmc.createNode("multiplyDivide", n="{0}_ik_stretch_value_MDV".format(name))
        stretch_condition = pmc.createNode("condition", n="{0}_ik_stretch_CONDITION".format(name))
        global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]
        base_length = pmc.createNode("plusMinusAverage", n="{0}_ik_base_length_PMA".format(name))

        start_loc.getShape().worldPosition[0] >> length_measure.startPoint
        end_loc.getShape().worldPosition[0] >> length_measure.endPoint
        ik_global_scale.setAttr("operation", 2)
        length_measure.distance >> ik_global_scale.input1X
        global_scale.output >> ik_global_scale.input2X
        ik_stretch_value.setAttr("operation", 2)
        # ik_stretch_value.setAttr("input2X", length_measure.getAttr("distance"))
        base_length.output1D >> ik_stretch_value.input2X
        ik_global_scale.outputX >> ik_stretch_value.input1X
        stretch_condition.setAttr("operation", 4)
        # stretch_condition.setAttr("secondTerm", length_measure.getAttr("distance"))
        base_length.output1D >> stretch_condition.secondTerm
        stretch_condition.setAttr("colorIfTrueR", 1)
        ik_global_scale.outputX >> stretch_condition.firstTerm
        ik_stretch_value.outputX >> stretch_condition.colorIfFalseR

        for i, ctrl in enumerate(fk_ctrls):
            if i > 0:
                ctrl.addAttr("baseTranslateY", attributeType="float",
                             defaultValue=pmc.xform(ctrl, q=1, translation=1)[1], hidden=0, keyable=0)
                ctrl.setAttr("baseTranslateY", lock=1, channelBox=0)
                fk_ctrls[i - 1].addAttr("stretch", attributeType="float", defaultValue=1, hidden=0, keyable=1,
                                        hasMinValue=1, minValue=0)
                jnt_length = pmc.createNode("multiplyDivide", n="{0}_jnt_{1}_length_MDV".format(name, i-1))
                ctrl.baseTranslateY >> jnt_length.input1Y
                fk_ctrls[i - 1].stretch >> jnt_length.input2Y
                if ctrl.getAttr("baseTranslateY") < 0:
                    absolute_base_length_value = pmc.createNode("multDoubleLinear",
                                                                n="{0}_jnt_{1}_invertLengthValue_MDL".format(name, i-1))
                    jnt_length.outputY >> absolute_base_length_value.input1
                    absolute_base_length_value.setAttr("input2", -1)
                    absolute_base_length_value.output >> base_length.input1D[i-1]
                else:
                    jnt_length.outputY >> base_length.input1D[i-1]

                jnt_ik_stretch = pmc.createNode("multiplyDivide", n="{0}_jnt_ik_{1}_stretch_MDV".format(name, i-1))
                jnt_length.outputY >> jnt_ik_stretch.input1Y
                stretch_condition.outColorR >> jnt_ik_stretch.input2Y

                blend = pmc.createNode("blendColors", n="{0}_jnt_{1}_fk_ik_stretch_merge_BLENDCOLOR".format(name, i-1))
                option_ctrl.fkIk >> blend.blender
                jnt_ik_stretch.outputY >> blend.color1R
                jnt_length.outputY >> blend.color2R
                blend.outputR >> ctrl.translateY
                blend.outputR >> skn_jnts[i].translateY

        ik_ctrl.setAttr("translate", ik_ctrl_translate)
        ik_ctrl.setAttr("rotate", ik_ctrl_rotate)

    def connect_quadruped_one_chain_fk_ik_stretch(self, fk_ctrls, ik_ctrl, option_ctrl, ik_setup_chain, skn_jnts, side_coef, name=None, finger=False):
        if name is None:
            name = self.model.module_name

        ik_ctrl_translate = ik_ctrl.getAttr("translate")
        ik_ctrl_rotate = ik_ctrl.getAttr("rotate")
        ik_ctrl.setAttr("translate", (0, 0, 0))
        ik_ctrl.setAttr("rotate", (0, 0, 0))

        if pmc.objExists("{0}_ik_length_start_LOC".format(name)):
            start_loc = pmc.ls("{0}_ik_length_start_LOC".format(name))[0]
        else:
            start_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_start_LOC".format(name))
            if finger:
                pmc.parent(start_loc, fk_ctrls[0], r=1)
                pmc.parent(start_loc, fk_ctrls[0].getParent(), r=0)
            else:
                pmc.parent(start_loc, fk_ctrls[0].getParent(), r=1)
            start_loc.setAttr("visibility", 0)
        if pmc.objExists("{0}_ik_length_end_LOC".format(name)):
            end_loc = pmc.ls("{0}_ik_length_end_LOC".format(name))[0]
        else:
            end_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_end_LOC".format(name))
            pmc.parent(end_loc, ik_ctrl, r=1)
            end_loc.setAttr("visibility", 0)

        if pmc.objExists("{0}_ik_length_measure_DDMShape".format(name)):
            length_measure = pmc.ls("{0}_ik_length_measure_DDMShape".format(name))[0]
        else:
            length_measure = pmc.createNode("distanceDimShape",
                                            n="{0}_ik_length_measure_DDMShape".format(name))
            length_measure.getParent().rename("{0}_ik_length_measure_DDM".format(name))
            pmc.parent(length_measure.getParent(), self.parts_grp, r=0)

            start_loc.getShape().worldPosition[0] >> length_measure.startPoint
            end_loc.getShape().worldPosition[0] >> length_measure.endPoint

        global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]

        if pmc.objExists("{0}_ik_global_scale_MDV".format(name)):
            ik_global_scale = pmc.ls("{0}_ik_global_scale_MDV".format(name))[0]
        else:
            ik_global_scale = pmc.createNode("multiplyDivide", n="{0}_ik_global_scale_MDV".format(name))

            ik_global_scale.setAttr("operation", 2)
            length_measure.distance >> ik_global_scale.input1X
            global_scale.output >> ik_global_scale.input2X

        if pmc.objExists("{0}_ik_base_length_PMA".format(name)):
            base_length = pmc.ls("{0}_ik_base_length_PMA".format(name))[0]
        else:
            base_length = pmc.createNode("plusMinusAverage", n="{0}_ik_base_length_PMA".format(name))

        if pmc.objExists("{0}_ik_stretch_value_MDV".format(name)):
            ik_stretch_value = pmc.ls("{0}_ik_stretch_value_MDV".format(name))[0]
        else:
            ik_stretch_value = pmc.createNode("multiplyDivide",
                                              n="{0}_ik_stretch_value_MDV".format(name))

            ik_stretch_value.setAttr("operation", 2)
            # ik_stretch_value.setAttr("input2X", length_measure.getAttr("distance"))
            base_length.output1D >> ik_stretch_value.input2X
            ik_global_scale.outputX >> ik_stretch_value.input1X

        stretch_condition = pmc.createNode("condition", n="{0}_ik_stretch_CONDITION".format(name))

        stretch_condition.setAttr("operation", 4)
        # stretch_condition.setAttr("secondTerm", length_measure.getAttr("distance"))
        base_length.output1D >> stretch_condition.secondTerm
        stretch_condition.setAttr("colorIfTrueR", 1)
        ik_global_scale.outputX >> stretch_condition.firstTerm
        ik_stretch_value.outputX >> stretch_condition.colorIfFalseR

        for i, ctrl in enumerate(fk_ctrls):
            # if i > 0:
            #     ctrl.addAttr("baseTranslateY", attributeType="float",
            #                  defaultValue=pmc.xform(ctrl, q=1, translation=1)[1], hidden=0, keyable=0)
            #     ctrl.setAttr("baseTranslateY", lock=1, channelBox=0)
            #     fk_ctrls[i - 1].addAttr("stretch", attributeType="float", defaultValue=1, hidden=0, keyable=1,
            #                             hasMinValue=1, minValue=0)
            #     jnt_length = pmc.createNode("multiplyDivide",
            #                                 n="{0}_jnt_{1}_length_MDV".format(name, i - 1))
            #     ctrl.baseTranslateY >> jnt_length.input1Y
            #     fk_ctrls[i - 1].stretch >> jnt_length.input2Y
            #     if ctrl.getAttr("baseTranslateY") < 0:
            #         absolute_base_length_value = pmc.createNode("multDoubleLinear",
            #                                                     n="{0}_jnt_{1}_invertLengthValue_MDL".format(
            #                                                         name, i - 1))
            #         jnt_length.outputY >> absolute_base_length_value.input1
            #         absolute_base_length_value.setAttr("input2", -1)
            #         absolute_base_length_value.output >> base_length.input1D[i - 1]
            #     else:
            #         jnt_length.outputY >> base_length.input1D[i - 1]

            # jnt_ik_stretch = pmc.createNode("multiplyDivide",
            #                                 n="{0}_jnt_ik_{1}_stretch_MDV".format(name, i - 1))
            # jnt_length.outputY >> jnt_ik_stretch.input1Y
            # stretch_condition.outColorR >> jnt_ik_stretch.input2Y

            # blend = pmc.createNode("blendColors",
            #                        n="{0}_jnt_{1}_fk_ik_stretch_merge_BLENDCOLOR".format(name, i - 1))
            # option_ctrl.fkIk >> blend.blender
            # jnt_ik_stretch.outputY >> blend.color1R
            # jnt_length.outputY >> blend.color2R
            # blend.outputR >> ctrl.translateY
            # blend.outputR >> ik_setup_chain[i].translateY
            # ctrl.translateY >> ik_setup_chain[i].translateY
            # blend.outputR >> skn_jnts[i].translateY

            # knee_ik_hdl = pmc.listRelatives(ik_setup_chain[-1], children=1, type="ikHandle")[0]
            # ankle_ik_hdl = pmc.listRelatives(ik_setup_chain[-2], children=1, type="ikHandle")[0]
            #
            # invert_node = pmc.createNode("multDoubleLinear", n="{0}_invert_translateY_MDL".format(knee_ik_hdl))
            #
            # ik_setup_chain[-1].translateY >> ankle_ik_hdl.translateY
            # ik_setup_chain[-1].translateY >> invert_node.input1
            # invert_node.setAttr("input2", -1)
            # invert_node.output >> knee_ik_hdl.translateY

            if i < (len(fk_ctrls) - 1):
                if not pmc.attributeQuery("baseLength", node=ctrl, exists=1):
                    ctrl.addAttr("baseLength", attributeType="float",
                                 defaultValue=pmc.xform(fk_ctrls[i+1], q=1, translation=1)[1] * side_coef, hidden=0, keyable=0)
                    ctrl.setAttr("baseLength", lock=1, channelBox=0)
                if not pmc.attributeQuery("stretch", node=ctrl, exists=1):
                    ctrl.addAttr("stretch", attributeType="float", defaultValue=1, hidden=0, keyable=1,
                                 hasMinValue=1, minValue=0)

                if pmc.objExists("{0}_jnt_{1}_length_MDV".format(name, i)):
                    jnt_length = pmc.ls("{0}_jnt_{1}_length_MDV".format(name, i))[0]
                else:
                    jnt_length = pmc.createNode("multiplyDivide",
                                                n="{0}_jnt_{1}_length_MDV".format(name, i))

                    ctrl.baseLength >> jnt_length.input1Y
                    ctrl.stretch >> jnt_length.input2Y
                    jnt_length.outputY >> base_length.input1D[i]

                jnt_ik_stretch = pmc.createNode("multiplyDivide",
                                                n="{0}_jnt_ik_{1}_stretch_MDV".format(name, i))
                ctrl.stretch >> jnt_ik_stretch.input1Y
                stretch_condition.outColorR >> jnt_ik_stretch.input2Y

                blend = pmc.createNode("blendColors",
                                       n="{0}_jnt_{1}_fk_ik_stretch_merge_BLENDCOLOR".format(name,
                                                                                             i))

                option_ctrl.fkIk >> blend.blender
                jnt_ik_stretch.outputY >> blend.color1R
                ctrl.stretch >> blend.color2R
                # blend.outputR >> ctrl.scaleY
                # blend.outputR >> ik_setup_chain[i].scaleY
                # blend.outputR >> skn_jnts[i].scaleY

                fk_ctrls[i + 1].addAttr("baseTranslateY", attributeType="float",
                                      defaultValue=pmc.xform(fk_ctrls[i+1], q=1, translation=1)[1], hidden=0, keyable=0)
                fk_ctrls[i + 1].setAttr("baseTranslateY", lock=1, channelBox=0)

                mult = pmc.createNode("multDoubleLinear",
                                      n="{0}_jnt_{1}_translateY_scaled_Value_MDL".format(name, i+1))

                fk_ctrls[i+1].baseTranslateY >> mult.input1
                blend.outputR >> mult.input2
                mult.output >> fk_ctrls[i+1].translateY
                mult.output >> ik_setup_chain[i+1].translateY
                mult.output >> skn_jnts[i+1].translateY

        ankle_hdl = pmc.listRelatives(ik_setup_chain[-2], children=1, type="ikHandle")[0]
        knee_hdl = pmc.listRelatives(ik_setup_chain[-1], children=1, type="ikHandle")[0]

        ik_setup_chain[-1].translateY >> ankle_hdl.translateY

        jnt_ty_invert = pmc.createNode("multDoubleLinear", n="{0}_translateY_invert_Value_MDL".format(str(fk_ctrls[-1])))
        jnt_ty_invert.setAttr("input2", -1)
        ik_setup_chain[-1].translateY >> jnt_ty_invert.input1
        jnt_ty_invert.output >> knee_hdl.translateY

        # ik_setup_chain[-2].scaleY >> ik_setup_chain[-1].scaleY

        ik_ctrl.setAttr("translate", ik_ctrl_translate)
        ik_ctrl.setAttr("rotate", ik_ctrl_rotate)

    def connect_one_jnt_ik_stretch(self, jnt, start_parent, end_parent):
        # jnt_stretch_mult_list = []
        # for i, jnt in enumerate(created_ik_jnts):
        #     if i != 0:
        jnt.addAttr("baseTranslateY", attributeType="float",
                    defaultValue=(pmc.xform(jnt, q=1, translation=1)[1]), hidden=0, keyable=0)
        jnt.setAttr("baseTranslateY", lock=1, channelBox=0)
        jnt_stretch_mult = pmc.createNode("multDoubleLinear",
                                          n="{0}_ik_stretch_mult_MDL".format(jnt))
                # jnt_stretch_mult_list.append(jnt_stretch_mult)

        # created_ik_ctrls[0].setAttr("translate", (0, 0, 0))
        # created_ik_ctrls[0].setAttr("rotate", (0, 0, 0))
        start_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_start_LOC".format(jnt))
        end_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_end_LOC".format(jnt))
        pmc.parent(start_loc, start_parent, r=1)
        pmc.parent(end_loc, end_parent, r=1)
        start_loc_shape = start_loc.getShape()
        end_loc_shape = end_loc.getShape()
        length_measure = pmc.createNode("distanceDimShape",
                                        n="{0}_ik_length_measure_DDMShape".format(jnt))
        measure_transform = length_measure.getParent()
        measure_transform.rename("{0}_ik_length_measure_DDM".format(jnt))
        pmc.parent(measure_transform, self.parts_grp, r=0)
        ik_global_scale = pmc.createNode("multiplyDivide", n="{0}_ik_global_scale_MDV".format(jnt))
        ik_stretch_value = pmc.createNode("multiplyDivide", n="{0}_ik_stretch_value_MDV".format(jnt))
        # stretch_condition = pmc.createNode("condition", n="{0}_ik_stretch_CONDITION".format(jnt))
        global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]

        start_loc_shape.worldPosition[0] >> length_measure.startPoint
        end_loc_shape.worldPosition[0] >> length_measure.endPoint
        ik_global_scale.setAttr("operation", 2)
        length_measure.distance >> ik_global_scale.input1X
        global_scale.output >> ik_global_scale.input2X
        ik_stretch_value.setAttr("operation", 2)
        ik_stretch_value.setAttr("input2X", length_measure.getAttr("distance"))
        ik_global_scale.outputX >> ik_stretch_value.input1X
        # stretch_condition.setAttr("operation", 4)
        # stretch_condition.setAttr("secondTerm", length_measure.getAttr("distance"))
        # stretch_condition.setAttr("colorIfTrueR", 1)
        # ik_global_scale.outputX >> stretch_condition.firstTerm
        # ik_stretch_value.outputX >> stretch_condition.colorIfFalseR
        # for i, jnt in enumerate(created_ik_jnts):
        #     if i != 0:
        #         stretch_condition.outColorR >> jnt_stretch_mult_list[i - 1].input1
        ik_stretch_value.outputX >> jnt_stretch_mult.input1
        #         jnt.baseTranslateY >> jnt_stretch_mult_list[i - 1].input2
        jnt.baseTranslateY >> jnt_stretch_mult.input2
        #         jnt_stretch_mult_list[i - 1].output >> jnt.translateY
        jnt_stretch_mult.output >> jnt.translateY

        start_loc_shape.setAttr("visibility", 0)
        end_loc_shape.setAttr("visibility", 0)

    def create_deformation_chain(self, name, start_parent, end_parent, start_ctrl, end_ctrl, option_ctrl,  how_many_jnts, side_coef):
        start_loc = pmc.spaceLocator(p=(0, 0, 0),
                                     n="{0}_ik_spline_start_LOC".format(name))
        start_tang = pmc.spaceLocator(p=(0, 0, 0),
                                      n="{0}_ik_spline_start_tangent_LOC".format(name))
        end_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_spline_end_LOC".format(name))
        end_tang = pmc.spaceLocator(p=(0, 0, 0),
                                    n="{0}_ik_spline_end_tangent_LOC".format(name))

        pmc.parent(start_loc, start_parent, r=1)
        pmc.parent(start_tang, start_parent, r=1)
        pmc.parent(end_loc, end_parent, r=1)
        pmc.parent(end_tang, end_parent, r=1)

        out_tang_name = str(start_ctrl).replace("fk_CTRL", "outTangent")
        in_tang_name = str(end_ctrl).replace("fk_CTRL", "inTangent")
        option_ctrl.addAttr(out_tang_name, attributeType="float", defaultValue=0.001, hidden=0, keyable=1,
                            hasMinValue=1, minValue=0.001)
        option_ctrl.addAttr(in_tang_name, attributeType="float", defaultValue=-0.001, hidden=0, keyable=1,
                            hasMaxValue=1, maxValue=-0.001)

        # start_ctrl.addAttr("outTangent", attributeType="float", defaultValue=0.001, hidden=0, keyable=1,
        #                    hasMinValue=1, minValue=0.001)
        # end_ctrl.addAttr("inTangent", attributeType="float", defaultValue=-0.001, hidden=0, keyable=1,
        #                  hasMaxValue=1, maxValue=-0.001)
        if side_coef == -1:
            outtangent_invert_node = pmc.createNode("multDoubleLinear", n="{0}_outTangent_invert_MDL".format(start_ctrl))
            intangent_invert_node = pmc.createNode("multDoubleLinear", n="{0}_inTangent_invert_MDL".format(end_ctrl))
            # start_ctrl.outTangent >> outtangent_invert_node.input1
            option_ctrl.connectAttr("{0}".format(out_tang_name), outtangent_invert_node.input1)
            outtangent_invert_node.setAttr("input2", -1)
            # end_ctrl.inTangent >> intangent_invert_node.input1
            option_ctrl.connectAttr("{0}".format(in_tang_name), intangent_invert_node.input1)
            intangent_invert_node.setAttr("input2", -1)
            outtangent_invert_node.output >> start_tang.translateY
            intangent_invert_node.output >> end_tang.translateY
        else:
            # start_ctrl.outTangent >> start_tang.translateY
            option_ctrl.connectAttr("{0}".format(out_tang_name), start_tang.translateY)
            # end_ctrl.inTangent >> end_tang.translateY
            option_ctrl.connectAttr("{0}".format(in_tang_name), end_tang.translateY)

        crv = create_curve_guide(3, 2, "{0}_ik_spline_CRV".format(name))

        start_loc.getShape().worldPosition >> crv.getShape().controlPoints[0]
        start_tang.getShape().worldPosition >> crv.getShape().controlPoints[1]
        end_loc.getShape().worldPosition >> crv.getShape().controlPoints[3]
        end_tang.getShape().worldPosition >> crv.getShape().controlPoints[2]

        chain_jnts = []
        for i in range(how_many_jnts + 1):
            distance = pmc.createNode("distanceBetween", n="temp_start_and_end_ik_spline_distanceBetween")
            start_loc.getShape().worldPosition >> distance.point1
            end_loc.getShape().worldPosition >> distance.point2
            if i == 0:
                pmc.select(cl=1)
            else:
                pmc.select(chain_jnts[i-1])
            jnt = pmc.joint(p=(0, (distance.getAttr("distance") / how_many_jnts * i)*side_coef, 0),
                            n="{0}_{1}_SKN".format(name, i))
            chain_jnts.append(jnt)
            pmc.delete(distance)

        chain_jnts[0].rename(str(chain_jnts[0].replace("_SKN", "_JNT")))
        chain_jnts[-1].rename(str(chain_jnts[-1].replace("_SKN", "_JNT")))

        ik_handle = pmc.ikHandle(n=("{0}_ik_spline_HDL".format(name)),
                                 startJoint=chain_jnts[0], endEffector=chain_jnts[-1],
                                 solver="ikSplineSolver", curve=crv, createCurve=False, parentCurve=False)[0]

        ik_effector = pmc.listRelatives(chain_jnts[-2], children=1)[-1]
        ik_effector.rename("{0}ik_spline_EFF".format(name))
        # pmc.disconnectAttr(ik_effector, inputs=1, outputs=0)
        pmc.parent(ik_effector, chain_jnts[-1], r=1)

        ik_handle.setAttr("dTwistControlEnable", 1)
        ik_handle.setAttr("dWorldUpType", 4)
        if side_coef == -1:
            ik_handle.setAttr("dForwardAxis", 3)
        else:
            ik_handle.setAttr("dForwardAxis", 2)
        ik_handle.setAttr("dWorldUpAxis", 6)
        ik_handle.setAttr("dWorldUpVectorX", 1)
        ik_handle.setAttr("dWorldUpVectorY", 0)
        ik_handle.setAttr("dWorldUpVectorZ", 0)
        ik_handle.setAttr("dWorldUpVectorEndX", 1)
        ik_handle.setAttr("dWorldUpVectorEndY", 0)
        ik_handle.setAttr("dWorldUpVectorEndZ", 0)
        start_loc.worldMatrix[0] >> ik_handle.dWorldUpMatrix
        end_loc.worldMatrix[0] >> ik_handle.dWorldUpMatrixEnd

        self.connect_ik_spline_stretch(crv, chain_jnts, measure_type="accurate")

        pmc.parent(ik_handle, self.parts_grp)
        pmc.parent(crv, self.parts_grp)
        pmc.parent(chain_jnts[0], self.jnt_input_grp)
        return chain_jnts


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


def z_box_curve(name):
    crv = pmc.curve(d=1, p=[(-3, 3, 1), (-3, 3, -1), (-3, -3, -1), (-3, -3, 1), (-3, 3, 1), (3, 3, 1), (3, -3, 1),
                            (-3, -3, 1), (-3, -3, -1), (3, -3, -1), (3, 3, -1), (-3, 3, -1), (-3, -3, -1), (3, -3, -1),
                            (3, -3, 1), (3, 3, 1), (3, 3, -1)], n=name)
    return crv


def large_box_curve(name):
    crv = pmc.curve(d=1, p=[(-4, 1.5, 4), (-4, 1.5, -4), (-4, -1.5, -4), (-4, -1.5, 4), (-4, 1.5, 4), (4, 1.5, 4),
                            (4, -1.5, 4), (-4, -1.5, 4), (-4, -1.5, -4), (4, -1.5, -4), (4, 1.5, -4), (-4, 1.5, -4),
                            (-4, -1.5, -4), (4, -1.5, -4), (4, -1.5, 4), (4, 1.5, 4), (4, 1.5, -4)], n=name)
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


def large_cube(name):
    crv = pmc.curve(d=1, p=[(-3, 3, 3), (-3, 3, -3), (-3, -3, -3), (-3, -3, 3), (-3, 3, 3), (3, 3, 3), (3, -3, 3),
                            (-3, -3, 3), (-3, -3, -3), (3, -3, -3), (3, 3, -3), (-3, 3, -3), (-3, -3, -3), (3, -3, -3),
                            (3, -3, 3), (3, 3, 3), (3, 3, -3)], n=name)
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


def signature_shape_curve(name):
    crv = pmc.curve(d=1, p=[(-10, 0, 0), (-8, 0, -8), (-6, 0, -8), (-5, 0, -4), (-9, 0, -4), (-5, 0, -4), (-4, 0, 0),
                            (-2, 0, 0), (-2, 0, -7), (-2, 0, 0), (0, 0, 0), (0, 0, -4), (3, 0, -4), (3, 0, -2),
                            (0, 0, -2), (0, 0, 0), (4, 0, 0), (8, 0, -4), (6, 0, -2), (4, 0, -4), (8, 0, 0), (14, 0, 0),
                            (14, 0, -8), (17, 0, -8), (18, 0, -7), (18, 0, -5), (17, 0, -4), (19, 0, -3), (19, 0, -1),
                            (18, 0, 0), (14, 0, 0), (20, 0, 0), (20, 0, -4), (20, 0, -3), (21, 0, -4), (22, 0, -4),
                            (23, 0, -3), (23, 0, -2), (23, 0, -3), (22, 0, -4), (21, 0, -4), (20, 0, -3), (20, 0, 0),
                            (25, 0, 0), (24, 0, -1), (24, 0, -3), (25, 0, -4), (26, 0, -4), (27, 0, -3), (27, 0, -1),
                            (26, 0, 0), (25, 0, 0), (29, 0, 0), (28, 0, -1), (29, 0, 0), (30, 0, 0), (31, 0, -1),
                            (28, 0, -3), (29, 0, -4), (30, 0, -4), (31, 0, -3), (30, 0, -4), (29, 0, -4), (28, 0, -3),
                            (31, 0, -1), (30, 0, 0), (33, 0, 0), (32, 0, -1), (33, 0, 0), (34, 0, 0), (35, 0, -1),
                            (32, 0, -3), (33, 0, -4), (34, 0, -4), (35, 0, -3), (34, 0, -4), (33, 0, -4), (32, 0, -3),
                            (35, 0, -1), (34, 0, 0), (37, 0, 0), (36, 0, -1), (36, 0, -3), (37, 0, -4), (39, 0, -4),
                            (39, 0, -1), (38, 0, 0), (37, 0, 0), (38, 0, 0), (39, 0, -1), (39, 0, 0), (40, 0, 0),
                            (40, 0, -4), (40, 0, -3), (41, 0, -4), (42, 0, -4), (43, 0, -3), (43, 0, -2), (43, 0, -3),
                            (42, 0, -4), (41, 0, -4), (40, 0, -3), (40, 0, 0), (45, 0, 0), (44, 0, -1), (44, 0, -3),
                            (45, 0, -4), (46, 0, -4), (47, 0, -3), (47, 0, -7), (47, 0, 0), (47, 0, -1), (46, 0, 0),
                            (45, 0, 0)], n=name)
    return crv


def stick_ball(name):
    crv = pmc.curve(d=1, p=[(0, 0, 0), (0, 0, -5), (-0.309017, 0, -5.048944), (-0.587785, 0, -5.190983),
                   (-0.809017, 0, -5.412215), (-0.951057, 0, -5.690983), (-1, 0, -6), (-0.951057, 0, -6.309017),
                   (-0.809017, 0, -6.587785), (-0.587785, 0, -6.809017), (-0.309017, 0, -6.951057), (0, 0, -7),
                   (0.309017, 0, -6.951057), (0.587786, 0, -6.809018), (0.809018, 0, -6.587786), (0.951057, 0, -6.309017),
                   (1, 0, -6), (0.951057, 0, -5.690983), (0.809017, 0, -5.412215), (0.587785, 0, -5.190983),
                   (0.309017, 0, -5.048944), (0, 0, -5), (0, 0.309017, -5.048944), (0, 0.587785, -5.190983),
                   (0, 0.809017, -5.412215), (0, 0.951057, -5.690983), (0, 1, -6), (0, 0.951057, -6.309017),
                   (0, 0.809017, -6.587785), (0, 0.587785, -6.809017), (0, 0.309017, -6.951057), (0, 0, -7),
                   (0, -0.309017, -6.951057), (0, -0.587786, -6.809018), (0, -0.809018, -6.587786), (0, -0.951057, -6.309017),
                   (0, -1, -6), (-0.309017, -0.951057, -6), (-0.587785, -0.809017, -6), (-0.809017, -0.587785, -6),
                   (-0.951057, -0.309017, -6), (-1, 0, -6), (-0.951057, 0.309017, -6), (-0.809017, 0.587785, -6),
                   (-0.587785, 0.809017, -6), (-0.309017, 0.951057, -6), (0, 1, -6), (0.309017, 0.951057, -6),
                   (0.587785, 0.809017, -6), (0.809017, 0.587785, -6), (0.951057, 0.309017, -6), (1, 0, -6),
                   (0.951057, -0.309017, -6), (0.809017, -0.587786, -6), (0.587786, -0.809018, -6), (0.309017, -0.951057, -6),
                   (0, -1, -6), (0, -0.951057, -5.690983), (0, -0.809017, -5.412215), (0, -0.587785, -5.190983),
                   (0, -0.309017, -5.048944), (0, 0, -5)], n=name)
    return crv


def oval_curve_x(name, side=1):
    crv = pmc.curve(d=3, p=[(0, 1 * side, 0), (0.0624626 * side, 1 * side, -0.0470694),
                            (0.187388 * side, 1 * side, -0.141208), (1.007808 * side, 1 * side, -0.199698),
                            (1.781381 * side, 1 * side, -0.141208), (2 * side, 1 * side, 0),
                            (1.781381 * side, 1 * side, 0.141208), (1.007808 * side, 1 * side, 0.199698),
                            (0.187388 * side, 1 * side, 0.141208), (0.0624626 * side, 1 * side, 0.0470694),
                            (0 * side, 1 * side, 0)], n=name)
    return crv


def oval_curve_y(name, side=1):
    crv = pmc.curve(d=3, p=[(-1 * side, 0 * side, 0), (-1 * side, 0.0624626 * side, -0.0470694),
                            (-1 * side, 0.187388 * side, -0.141208), (-1 * side, 1.007808 * side, -0.199698),
                            (-1 * side, 1.781381 * side, -0.141208), (-1 * side, 2 * side, 0),
                            (-1 * side, 1.781381 * side, 0.141208), (-1 * side, 1.007808 * side, 0.199698),
                            (-1 * side, 0.187388 * side, 0.141208), (-1 * side, 0.0624626 * side, 0.0470694),
                            (-1 * side, 0 * side, 0)], n=name)
    return crv


def oval_curve_z(name, side=1):
    crv = pmc.curve(d=3, p=[(0, 0 * side, 1 * side), (-0.0470694, 0.0624626 * side, 1 * side),
                            (-0.141208, 0.187388 * side, 1 * side), (-0.199698, 1.007808 * side, 1 * side),
                            (-0.141208, 1.781381 * side, 1 * side), (0, 2 * side, 1 * side),
                            (0.141208, 1.781381 * side, 1 * side), (0.199698, 1.007808 * side, 1 * side),
                            (0.141208, 0.187388 * side, 1 * side), (0.0470694, 0.0624626 * side, 1 * side),
                            (0, 0 * side, 1 * side)], n=name)
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
    """ 2=dark_grey, 3=light_grey, 6=blue, 9=purple, 13=red, 14=green, 17=yellow, 20=pink """
    if isinstance(selection, list):
        for obj in selection:
            if pmc.nodeType(obj) == "nurbsCurve":
                shape = obj
            else:
                shape = obj.getShape()

            if shape is not None:
                pmc.setAttr(shape + ".overrideEnabled", 1)
                pmc.setAttr(shape + ".overrideColor", color)
            if pmc.nodeType(obj) == "joint":
                pmc.setAttr(obj + ".overrideEnabled", 1)
                pmc.setAttr(obj + ".overrideColor", color)
    else:
        if pmc.nodeType(selection) == "nurbsCurve":
            shape = selection
        else:
            shape = selection.getShape()
        if shape is not None:
            pmc.setAttr(shape + ".overrideEnabled", 1)
            pmc.setAttr(shape + ".overrideColor", color)
        if pmc.nodeType(selection) == "joint":
            pmc.setAttr(selection + ".overrideEnabled", 1)
            pmc.setAttr(selection + ".overrideColor", color)


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


def create_curve_guide(d, number_of_points, name, hauteur_curve=10, front_axe="y"):
    if front_axe == "x":
        crv = pmc.curve(d=1, p=[(0, 0, 0), (hauteur_curve/2, 0, 0), (hauteur_curve, 0, 0)], k=[0, 1, 2])
    elif front_axe == "z":
        crv = pmc.curve(d=1, p=[(0, 0, 0), (0, 0, hauteur_curve / 2), (0, 0, hauteur_curve)], k=[0, 1, 2])
    else:
        crv = pmc.curve(d=1, p=[(0, 0, 0), (0, hauteur_curve / 2, 0), (0, hauteur_curve, 0)], k=[0, 1, 2])

    if d == 1 and number_of_points == 3:
        crv_rebuilded = crv
    elif d == 2:
        crv_rebuilded = pmc.rebuildCurve(crv, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                         s=3, d=d, ch=0, replaceOriginal=1)[0]
        pmc.delete(crv_rebuilded.cv[-2])
        pmc.delete(crv_rebuilded.cv[1])
    else:
        crv_rebuilded = pmc.rebuildCurve(crv, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0, s=(number_of_points - 1),
                                         d=d, ch=0, replaceOriginal=1)[0]
    crv_rebuilded.rename(name)
    return crv_rebuilded


def create_jnts_from_cv_list_and_return_jnts_list(vertex_list, module_name, forward_axis="y"):
    pmc.select(cl=1)
    loc_list = []
    created_jnts_list = []
    for i, vertex in enumerate(vertex_list):
        loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_tempLOC".format(vertex))
        loc.setAttr("translate", pmc.xform(vertex, q=1, ws=1, translation=1))
        if i > 0:
            if forward_axis == "z":
                const = pmc.aimConstraint(loc, loc_list[i - 1], maintainOffset=0,
                                          aimVector=(0.0, 0.0, 1.0),
                                          upVector=(0.0, 1.0, 0.0), worldUpType="vector", worldUpVector=(0.0, 1.0, 0.0))
            else:
                const = pmc.aimConstraint(loc, loc_list[i-1], maintainOffset=0,
                                          aimVector=(0.0, 1.0, 0.0),
                                          upVector=(0.0, 0.0, 1.0), worldUpType="vector", worldUpVector=(0.0, 0.0, 1.0))
            pmc.delete(const)
            pmc.parent(loc, loc_list[i-1], r=0)
        loc_list.append(loc)

    pmc.select(cl=1)
    for i, loc in enumerate(loc_list):
        jnt = pmc.joint(p=(pmc.xform(loc, q=1, ws=1, translation=1)),
                        o=(pmc.xform(loc, q=1, rotation=1)),
                        n="{0}_{1}_JNT".format(module_name, i), rad=0.5)
        created_jnts_list.append(jnt)

    created_jnts_list[-1].setAttr("jointOrient", (0, 0, 0))
    created_jnts_list[-1].rename("{0}_end_JNT".format(module_name))
    pmc.delete(loc_list[0])
    return created_jnts_list


def change_jnt_chain_suffix(jnts_chain, new_suffix):
    for jnt in jnts_chain:
        jnt_name = jnt.name().rsplit("|")[-1]
        split_name = jnt_name.rsplit("_")
        split_name.pop(-1)
        new_suffix_list = [new_suffix]
        new_name = "_".join(split_name + new_suffix_list)
        jnt.rename(new_name)


def clean_ctrl(ctrl, color_value, trs="trs", visibility_dependence=None):
        change_shape_color(ctrl, color_value)

        for attr in [x + y for x in trs.lower() for y in "xyz"]:
            ctrl.setAttr(attr, lock=True, keyable=False, channelBox=False)

        if pmc.nodeType(ctrl) == "joint":
            ctrl.setAttr("radius", lock=True, keyable=False, channelBox=False)

        ctrl_ofs = ctrl.getParent()
        if pmc.nodeType(ctrl_ofs) == "transform":
            ctrl_ofs.setAttr("translateX", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("translateY", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)

        if visibility_dependence is not None:
            pmc.connectAttr(visibility_dependence, ctrl.visibility)


def create_output(name, parent):
    output = pmc.spaceLocator(p=(0, 0, 0), n=name)
    pmc.parent(output, parent, r=1)
    output.visibility.set(0)
    return output


def raz_fk_ctrl_rotate(ctrl, jnt, stretch=False):
    pmc.select(cl=1)
    jnt_ofs = pmc.joint(p=(0, 0, 0), n="{0}_RAZ".format(ctrl))
    jnt_ofs.setAttr("rotateOrder", 4)
    jnt_ofs.setAttr("drawStyle", 2)
    pmc.parent(jnt_ofs, ctrl.getParent(), r=1)
    pmc.reorder(jnt_ofs, front=1)
    jnt_ofs.setAttr("translate", ctrl.getAttr("translate"))
    jnt_ofs.setAttr("jointOrient", ctrl.getAttr("jointOrient"))
    jnt_ofs.setAttr("rotate", ctrl.getAttr("rotate"))
    pmc.parent(ctrl, jnt_ofs, r=0)

    if stretch and pmc.listConnections(ctrl.ty, destination=0, source=1) != []:
        stretch_node = pmc.listConnections(ctrl.ty, destination=0, source=1)[0]
        stretch_node.output // ctrl.ty
        stretch_node.output >> jnt_ofs.ty

    ctrl.setAttr("translate", (0, 0, 0))
    ctrl.setAttr("rotate", (0, 0, 0))
    ctrl.setAttr("jointOrient", (0, 0, 0))

    jnt_offset = pmc.createNode("plusMinusAverage", n="{0}_raz_jnt_offset_PMA".format(ctrl))
    jnt_offset.setAttr("operation", 1)
    ctrl.rotate >> jnt_offset.input3D[0]
    jnt_ofs.rotate >> jnt_offset.input3D[1]
    jnt_offset.output3D >> jnt.rotate

    ctrl_cvs = ctrl.cv[:]
    for i, cv in enumerate(ctrl_cvs):
        pmc.xform(ctrl.getShape().controlPoints[i], ws=1, translation=(pmc.xform(cv, q=1, ws=1, translation=1)[0],
                                                                       pmc.xform(ctrl, q=1, ws=1, translation=1)[1],
                                                                       pmc.xform(cv, q=1, ws=1, translation=1)[2]))

    clean_ctrl(jnt_ofs, 0, trs="trs")

#
# def raz_ik_ctrl_translate(ctrl):
#     raz = pmc.group(em=1, n="{0}_RAZ".format(ctrl))
#     pmc.parent(raz, ctrl.getParent(), r=1)
#     raz.setAttr("translate", ctrl.getAttr("translate"))
#     pmc.parent(ctrl, raz, r=1)
#     ctrl.setAttr("translate", (0, 0, 0))


def raz_ik_ctrl_translate_rotate(ctrl, jnt, side_coef):
    const = pmc.listRelatives(jnt, children=1, type="parentConstraint")[0]
    const.setAttr("target[0].targetOffsetRotate", (const.getAttr("target[0].targetOffsetRotateX") -
                                                   (pmc.xform(ctrl, q=1, rotation=1)[0] * side_coef),
                                                   const.getAttr("target[0].targetOffsetRotateY") -
                                                   (pmc.xform(ctrl, q=1, rotation=1)[1] * side_coef),
                                                   const.getAttr("target[0].targetOffsetRotateZ") +
                                                   pmc.xform(ctrl, q=1, rotation=1)[2]))
    pmc.xform(ctrl.getParent(), ws=1, translation=(pmc.xform(ctrl, q=1, ws=1, translation=1)))
    ctrl.setAttr("translate", (0, 0, 0))
    ctrl.setAttr("rotate", (0, 0, 0))
    ctrl.setAttr("jointOrient", (0, 0, 0))


def raz_one_chain_ik_ctrl_translate_rotate(ctrl):
    pmc.xform(ctrl.getParent(), ws=1, translation=(pmc.xform(ctrl, q=1, ws=1, translation=1)))
    ctrl.setAttr("translate", (0, 0, 0))
    ctrl.setAttr("rotate", (0, 0, 0))
    ctrl.setAttr("jointOrient", (0, 0, 0))


def raz_one_chain_ikfk_fk_ctrl_rotate(ctrl, skn_jnt=None, raz_ctrl_shape_axe="y"):
    loc = pmc.spaceLocator(p=(0, 0, 0), n="get_xyz_orient_temp_loc")

    pmc.parent(loc, ctrl, r=1)
    pmc.parent(loc, ctrl.getParent(), r=0)

    ctrl.setAttr("jointOrient", (loc.getAttr("rotateX"), loc.getAttr("rotateY"), loc.getAttr("rotateZ")))

    if skn_jnt:
        skn_jnt.disconnectAttr("jointOrient")
        ctrl.jointOrient >> skn_jnt.jointOrient

    ctrl.setAttr("rotate", (0, 0, 0))

    # VERY IMPORTANT IF YOU DONT WANT TO HAVE FUCKING FLIP IN YOUR JNT_CHAIN :
    ctrl.setAttr("preferredAngle", (0, 0, 0))

    if ctrl.getShape() is not None:
        ctrl_cvs = ctrl.cv[:]
        for i, cv in enumerate(ctrl_cvs):
            if raz_ctrl_shape_axe == "x":
                pmc.xform(ctrl.getShape().controlPoints[i], ws=1, translation=(pmc.xform(ctrl, q=1, ws=1, translation=1)[0],
                                                                               pmc.xform(cv, q=1, ws=1, translation=1)[1],
                                                                               pmc.xform(cv, q=1, ws=1, translation=1)[2]))
            elif raz_ctrl_shape_axe == "y":
                pmc.xform(ctrl.getShape().controlPoints[i], ws=1, translation=(pmc.xform(cv, q=1, ws=1, translation=1)[0],
                                                                               pmc.xform(ctrl, q=1, ws=1, translation=1)[1],
                                                                               pmc.xform(cv, q=1, ws=1, translation=1)[2]))
            elif raz_ctrl_shape_axe == "z":
                pmc.xform(ctrl.getShape().controlPoints[i], ws=1, translation=(pmc.xform(cv, q=1, ws=1, translation=1)[0],
                                                                               pmc.xform(cv, q=1, ws=1, translation=1)[1],
                                                                               pmc.xform(ctrl, q=1, ws=1, translation=1)[2]))

    pmc.delete(loc)


def create_jnttype_ctrl(name, shape, drawstyle=2, rotateorder=0):
    pmc.select(cl=1)
    ctrl = pmc.joint(p=(0, 0, 0), n=name)
    pmc.parent(shape.getShape(), ctrl, r=1, s=1)
    ctrl.getShape().rename("{0}Shape".format(ctrl))
    ctrl.setAttr("drawStyle", drawstyle)
    pmc.delete(shape)
    ctrl.setAttr("rotateOrder", rotateorder)
    return ctrl


def connect_condition_to_constraint(const_attr_to_connect_entire_name, space_attr, space_number, condition_name, switch=None):
    condition = pmc.createNode("condition", n=condition_name)
    condition.setAttr("operation", 0)
    condition.setAttr("firstTerm", space_number)
    space_attr >> condition.secondTerm
    condition.setAttr("colorIfTrueR", 1)
    condition.setAttr("colorIfFalseR", 0)
    if not switch:
        pmc.connectAttr("{0}.outColorR".format(condition), "{0}".format(const_attr_to_connect_entire_name))
    else:
        switch_node = pmc.createNode("multDoubleLinear", n="{0}".format(str(condition).replace("_COND", "_fkik_switch_MDL")))
        condition.outColorR >> switch_node.input1
        switch.output1D >> switch_node.input2
        pmc.connectAttr("{0}.output".format(switch_node), "{0}".format(const_attr_to_connect_entire_name))


def add_parameter_as_extra_attr(obj, parameter_name, parameter_value):
    obj.addAttr(parameter_name, dataType="string", hidden=0, keyable=0, readable=1, writable=1)
    obj.setAttr(parameter_name, str(parameter_value))
    obj.setAttr(parameter_name, lock=1)


def continuous_check_and_reorder_vertex_list(vertices_list, module_name):
    reordered_list = [vertices_list[0]]

    for i in range(len(vertices_list)):
        edges_from_point = pmc.ls(pmc.polyListComponentConversion(reordered_list[i], fromVertex=1, toEdge=1), flatten=1)
        vertices_from_edges = pmc.ls(pmc.polyListComponentConversion(edges_from_point, toVertex=1, fromEdge=1, border=1), flatten=1)
        next_vertex = [vertex for vertex in vertices_from_edges if (vertex in vertices_list and vertex not in reordered_list)]
        if len(next_vertex) == 0:
            break
        elif len(next_vertex) == 1:
            reordered_list.append(next_vertex[0])
        elif len(next_vertex) > 1:
            reordered_list.append(next_vertex[0])
            pmc.warning("for module \"{0}\", Risk that not all selected vertices were used to create the surface. Selection must form a continuous, non-branching path".format(module_name))

    if len(reordered_list) < len(vertices_list):
        pmc.warning("for module \"{0}\", Not all selected vertices were used to create the surface. Selection must form a continuous, non-branching path".format(module_name))

    return reordered_list
