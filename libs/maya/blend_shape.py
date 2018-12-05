# -*- coding: utf-8 -*-
u"""BlendShape関連"""
from __future__ import absolute_import, division, print_function

from squid.core.libs.maya import attribute

from maya import cmds


def get_all_blend_shapes():
    u"""シーン上の全てのblendShapeを返す

    Returns:
        list of unicode: blendShapeのリスト
    """
    return cmds.ls(type="blendShape")


def get_input_targets(blend_shapes):
    u"""指定blendShapeのinputTargetを返す

    Args:
        blend_shapes (list of unicode): blendShapeのリスト

    Returns:
        list of unicode: inputTargetのリスト
    """
    res = []
    if not blend_shapes:
        return res
    for blend in blend_shapes:
        input_targets = cmds.listConnections(attribute.convert_attribute(blend, attribute.INPUT_TARGET))
        if not input_targets:
            continue
        res.extend(input_targets)
    return res


def get_weight_members(blend_shape):
    u"""指定blendShapeのweightのメンバーを返す

    Args:
        blend_shape (unicode): blendShape

    Returns:
        list of unicode: 指定blendShapeのweightのメンバー
    """
    if not blend_shape:
        return []
    weights = cmds.listAttr(attribute.convert_attribute(blend_shape, attribute.WEIGHT), m=True)
    if not weights:
        return []
    return weights


def get_relative_blend_shapes(target, all_descendents=False, include_self=False):
    u"""指定ノード配下のblendShapeを返す

    Args:
        target (unicode): 対象のノード
        all_descendents (bool): 孫も対象とするかどうか
        include_self (bool): 自身も対象とするかどうか

    Returns:
        list of unicode: 指定ノード配下のblendShapeのリスト
    """
    blend_shapes = []
    if not target:
        return blend_shapes
    transforms = cmds.listRelatives(target, type="transform", ad=all_descendents, f=True)
    if transforms is None:
        transforms = []
    if include_self:
        transforms.append(target)
    for t in transforms:
        tmp_blend_shapes = cmds.ls(cmds.listHistory(t), type="blendShape", long=True)
        if not tmp_blend_shapes or len(tmp_blend_shapes) != 1:
            continue
        blend_shapes.append(tmp_blend_shapes[0])
    return blend_shapes


def delete_relative_blend_shape_input_targets(target, all_descendents=False, include_self=False):
    u"""指定ノード配下のblendShapeのinputTargetを削除する

    Args:
        target (unicode): 対象のノード
        all_descendents (bool): 孫も対象とするかどうか
        include_self (bool): 自身も対象とするかどうか
    """
    blend_shapes = get_relative_blend_shapes(target,
                                             all_descendents=all_descendents,
                                             include_self=include_self)
    if not blend_shapes:
        return
    input_targets = get_input_targets(blend_shapes)
    if not input_targets:
        return
    cmds.delete(input_targets)


def collect_relative_post_deformation_node(target, all_descendents=False, include_self=False):
    u"""指定ノード配下のpost-deformationになっているノードを収集

    Args:
        target (unicode): 対象のノード
        all_descendents (bool): 孫も対象とするかどうか
        include_self (bool): 自身も対象とするかどうか

    Returns:
        list of unicode: post-deformationになっているノードのリスト

    """
    return collect_post_deformation_node(get_relative_blend_shapes(target,
                                                                   all_descendents=all_descendents,
                                                                   include_self=include_self))


def collect_post_deformation_node(targets=None):
    u"""post-deformationになっているノードを収集

    Args:
        targets (list of unicode): 対象のblendShapeのリスト（指定されていなければシーンの全てのblendShape）

    Returns:
        list of unicode: post-deformationになっているノードのリスト
    """
    result = []
    if targets is None:
        targets = cmds.ls(type="blendShape")
    for b in targets:
        target = cmds.blendShape(b, q=True, g=True)[0]
        histories = cmds.listHistory(target, gl=True, pdo=True, lf=True, f=False, il=2)
        skin_cluster_found = False
        for h in histories:
            object_type = cmds.objectType(h)
            if object_type == "skinCluster":
                skin_cluster_found = True
                continue
            if object_type == "blendShape" and not skin_cluster_found:
                result.append(target)
                break
    return result
