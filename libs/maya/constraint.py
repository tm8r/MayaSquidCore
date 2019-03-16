# -*- coding: utf-8 -*-
u"""コンストレイント関連"""
from __future__ import absolute_import, division, print_function

from collections import defaultdict
from squid.vendor.enum import Enum

from squid.core.libs.maya import collector

from maya import cmds


class ConstraintType(Enum):
    u"""コンストレイントの種類"""

    parentConstraint = 0
    pointConstraint = 1
    orientConstraint = 2
    scaleConstraint = 3
    aimConstraint = 4

    @staticmethod
    def get_constraint_type(constraint_node):
        u"""コンストレイントノード名からコンストレイントの種類を返す

        Args:
            constraint_node (unicode): コンストレイントノード

        Returns:
            ConstraintType: コンストレイントの種類
        """
        for c in ConstraintType:
            if c.name in constraint_node:
                return c
        return None


def create_constraint(targets, node, constraint_type):
    u"""コンストレイントを作成

    Args:
        targets (list of unicode): ターゲットのリスト
        node (unicode): コンストレイント先
        constraint_type (ConstraintType): コンストレイントの種類

    """
    if constraint_type == ConstraintType.parentConstraint:
        cmds.parentConstraint(targets, node)
    elif constraint_type == ConstraintType.pointConstraint:
        cmds.pointConstraint(targets, node)
    elif constraint_type == ConstraintType.orientConstraint:
        cmds.orientConstraint(targets, node)
    elif constraint_type == ConstraintType.scaleConstraint:
        cmds.scaleConstraint(targets, node)
    elif constraint_type == ConstraintType.aimConstraint:
        cmds.aimConstraint(targets, node)


def get_constraint_members(node, constraint_type=None):
    u"""コンストレイントされているノードのリストを返す

    Args:
        node (unicode): 対象ノード
        constraint_type (ConstraintType): コンストレイントの種類

    Returns:
        list of unicode: コンストレイントされているノードのリスト
    """
    constraints = _get_constraints(node, constraint_type)
    if not constraints:
        return []
    res = []
    for c in constraints:
        members = cmds.listConnections(c + ".target")
        if not members:
            continue
        res.extend(list(set([x for x in members if x != collector.get_short_name(c)])))
    return res


def get_constraint_members_reverse(node, constraint_type=None):
    u"""コンストレイントしているノードのリストを返す

    Args:
        node (unicode): 対象ノード
        constraint_type (ConstraintType): コンストレイントの種類

    Returns:
        list of unicode: コンストレイントしているノードのリスト
    """
    constraints = _get_constraints_reverse(node, constraint_type)
    if not constraints:
        return []
    res = []
    for c in constraints:
        members = cmds.listRelatives(c, parent=True)
        res.extend(members)
    return res


def get_constraint_members_dict(node):
    u"""指定ノードのコンストレイントの種類ごとのコンストレイントされているノードの辞書を返す

    Args:
        node (unicode): 対象のノード

    Returns:
        dict: コンストレイントの種類ごとのコンストレイントされているノードの辞書
    """
    constraints = _get_constraints(node)
    res = defaultdict(list)
    if not constraints:
        return res
    for c in constraints:
        constraint_type = ConstraintType.get_constraint_type(c)
        if not constraint_type:
            continue
        members = cmds.listConnections(c + ".target")
        if not members:
            continue
        members = list(set([x for x in members if x != collector.get_short_name(c)]))
        res[constraint_type].extend(members)
    return res


def get_constraint_members_dict_reverse(node):
    u"""指定ノードのコンストレイントの種類ごとのコンストレイントされているノードの辞書を返す

    Args:
        node (unicode): 対象のノード

    Returns:
        dict: コンストレイントの種類ごとのコンストレイントされているノードの辞書
    """
    constraints = _get_constraints_reverse(node)
    res = defaultdict(list)
    if not constraints:
        return res
    for c in constraints:
        constraint_type = ConstraintType.get_constraint_type(c)
        if not constraint_type:
            continue
        members = cmds.listRelatives(c, parent=True)
        if not members:
            continue
        res[constraint_type].extend(members)
    return res


def _get_constraints(node, constraint_type=None):
    u"""コンストレイントノードのリストを返す

    Args:
        node (unicode): 対象ノード
        constraint_type (ConstraintType): コンストレイントの種類

    Returns:
        list of unicode: コンストレイントノードのリスト
    """
    constraints = cmds.listRelatives(node, type="constraint", f=True)
    if not constraints:
        return []
    constraints = list(set(constraints))
    if constraint_type:
        constraints = [x for x in constraints if constraint_type.name in x]
    return constraints


def _get_constraints_reverse(node, constraint_type=None):
    u"""コンストレイントノードのリストを返す（コンストレイントしている側から）

    Args:
        node (unicode): 対象ノード
        constraint_type (ConstraintType): コンストレイントの種類

    Returns:
        list of unicode: コンストレイントノードのリスト
    """
    constraints = cmds.listRelatives(node, type="constraint")
    if not constraints:
        constraints = []
    constraints = list(set(constraints))
    constraints_reverse = cmds.listConnections(node, type="constraint")

    if not constraints_reverse:
        return

    constraints_reverse = list(set([x for x in constraints_reverse if x not in constraints]))

    if constraint_type:
        constraints_reverse = [x for x in constraints_reverse if constraint_type.name in x]
    return constraints_reverse