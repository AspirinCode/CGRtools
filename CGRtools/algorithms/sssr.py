# -*- coding: utf-8 -*-
#
#  Copyright 2017-2019 Ramil Nugmanov <stsouko@live.ru>
#  This file is part of CGRtools.
#
#  CGRtools is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
from typing import Set, List
from ..cache import cached_property


class TickedPath:
    __slots__ = '__path', '__ticks'

    def __init__(self, root, first):
        self.__path = [root, first]
        self.__ticks = []

    def append(self, node):
        self.__path.append(node)

    def tick(self):
        self.__ticks.insert(0, len(self.__path))

    @property
    def paths(self):
        paths = [self.__path]
        for x in self.__ticks:
            paths.append(self.__path[:x])
        return paths

    @property
    def path(self):
        return self.__path

    @property
    def leaf(self):
        return self.__path[-1]

    @property
    def root(self):
        return self.__path[0]


class SSSR:
    """ SSSR calculation. based on idea of PID matrices from:
        Lee, C. J., Kang, Y.-M., Cho, K.-H., & No, K. T. (2009).
        A robust method for searching the smallest set of smallest rings with a path-included distance matrix.
        Proceedings of the National Academy of Sciences of the United States of America, 106(41), 17355–17358.
        http://doi.org/10.1073/pnas.0813040106
    """
    @cached_property
    def skin_atoms_set(self) -> Set[int]:
        adj = self._adj
        if len(adj) < 3:
            return set()

        atoms = {x for x, y in adj.items() if y}  # ignore isolated atoms
        terminals = {x for x, y in adj.items() if len(y) == 1}
        if terminals:
            bubble = terminals
            while True:
                bubble = {y for x in bubble for y in adj[x].keys() - terminals if len(adj[y].keys() - terminals) < 2}
                if not bubble:
                    break
                terminals.update(bubble)
            atoms.difference_update(terminals)  # skip not-cycle chains
        return atoms

    @cached_property
    def skin_atoms(self) -> List[int]:
        return list(self.skin_atoms_set)

    def _closures(self):
        adj = self._adj
        atoms = self.skin_atoms_set
        n_sssr = sum(1 for x in atoms for _ in adj[x].keys() & atoms) // 2 - len(atoms) + 1

        tail = atoms.pop()
        next_stack = {x: [TickedPath(tail, x)] for x in adj[tail].keys() & atoms}
        terminated = {}

        while True:
            next_front = set()
            found_odd = set()
            stack, next_stack = next_stack, {}
            for broom in stack.values():
                tail = broom[0].leaf
                next_front.add(tail)
                neighbors = adj[tail].keys() & atoms
                if len(neighbors) == 1:
                    n = neighbors.pop()
                    if n in found_odd:
                        continue
                    for branch in broom:
                        branch.append(n)

                    if n in stack:  # odd rings
                        found_odd.add(tail)
                        if n in next_stack:
                            next_stack[n].extend(broom)
                        else:
                            stack[n].extend(broom)  # not visited
                            terminated[n] = stack[n]
                    elif n in next_stack:  # even rings
                        next_stack[n].extend(broom)
                        if n not in terminated:
                            terminated[n] = next_stack[n]
                    else:
                        next_stack[n] = broom
                elif neighbors:
                    nn = neighbors.pop()  # extract
                    for n in neighbors:
                        if n in found_odd:
                            continue
                        next_broom = [[tail, n]]
                        for branch in broom:
                            next_broom.append(branch + [n])
                        if n in stack:  # odd rings
                            found_odd.add(tail)
                            if n in next_stack:
                                next_stack[n].extend(next_broom)
                            else:
                                stack[n].extend(next_broom)  # not visited
                                terminated[n] = stack[n]
                        elif n in next_stack:  # even rings
                            next_stack[n].extend(next_broom)
                            if n not in terminated:
                                terminated[n] = next_stack[n]
                        else:
                            next_stack[n] = next_broom

                    if nn in found_odd:
                        continue

            atoms.difference_update(next_front)
            if not atoms:
                break
            elif not next_stack:
                n_sssr += 1
                tail = atoms.pop()
                next_stack = {x: [[tail, x]] for x in adj[tail].keys() & atoms}
        return terminated, n_sssr

    @cached_property
    def sssr(self):
        if not self.skin_atoms_set:
            return []

        terminated, n_sssr = self._closures()
        if not n_sssr:
            return []

        pid1 = {}
        pid2 = {}
        for j, paths in terminated.items():
            for path in paths:
                i = path[0]
                k = (i, j)
                if k in pid1:
                    ls = len(pid1[k][0])
                    lp = len(path)
                    if lp == ls:
                        pid1[k].append(path)
                    elif ls - lp == 1:
                        pid2[k], pid1[k] = pid1[k], [path]
                    elif lp - ls == 1:
                        pid2[k].append(path)
                    elif lp < ls:
                        pid1[k] = [path]
                        pid2[k] = []
                else:
                    pid1[k] = [path]
                    pid2[k] = []

        c_set = []
        for k, p1ij in pid1.items():
            dij = len(p1ij[0]) * 2 - 2
            p2ij = pid2[k]
            if len(p1ij) == 1:  # one shortest
                if not p2ij:  # need shortest + 1 path
                    continue
                c_set.append((dij + 1, p1ij, p2ij))
            elif not p2ij:  # one or more odd rings
                c_set.append((dij, p1ij, None))
            else:  # odd and even rings found (e.g. bicycle)
                c_set.append((dij, p1ij, None))
                c_set.append((dij + 1, p1ij, p2ij))

        c_sssr = {}
        for c_num, p1ij, p2ij in sorted(c_set):
            if c_num % 2:  # odd rings
                c1 = p1ij[0]  # any shortest acceptable. sssr is not a unique set of rings
                c11 = c1[1]
                c12 = c1[-2]
                for c2 in p2ij:
                    if c11 == c2[1] or c12 == c2[-2]:
                        continue
                    c = c1 + c2[-2:0:-1]
                    ck = tuple(sorted(c))
                    if ck not in c_sssr:
                        c_sssr[ck] = c
                        if len(c_sssr) == n_sssr:
                            return list(c_sssr.values())
            else:
                for c1, c2 in zip(p1ij, p1ij[1:]):
                    if c1[1] == c2[1] or c1[-2] == c2[-2]:
                        continue
                    c = c1 + c2[-2:0:-1]
                    ck = tuple(sorted(c))
                    if ck not in c_sssr:
                        c_sssr[ck] = c
                        if len(c_sssr) == n_sssr:
                            return list(c_sssr.values())


__all__ = ['SSSR']
