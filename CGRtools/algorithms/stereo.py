# -*- coding: utf-8 -*-
#
#  Copyright 2019 Ramil Nugmanov <stsouko@live.ru>
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
from collections import defaultdict
from itertools import combinations, product
from .morgan import primes
from ..cache import cached_property


def _pyramid_volume(n, u, v, w):
    nx, ny, nz = n
    ux, uy, uz = u
    vx, vy, vz = v
    wx, wy, wz = w
    ux -= nx
    uy -= ny
    uz -= nz
    vx -= nx
    vy -= ny
    vz -= nz
    wx -= nx
    wy -= ny
    wz -= nz
    return ux * (vy * wz - vz * wy) + uy * (vz * wx - vx * wz) + uz * (vx * wy - vy * wx)


class Stereo:
    @cached_property
    def chiral_atoms(self):
        """
        dict of chiral atoms valued with ordered neighbors
        """
        print(self.__potentially_alkene)
        print(self.__potentially_tetrahedron)
        print(self.__potentially_atropisomer)
        return

    @cached_property
    def __potentially_alkene(self):
        # detect allenes and cis/trans double bonds.
        adj = defaultdict(list)  # carbon double bonds adjacency matrix
        for n, m, bond in self.bonds():
            if bond.order == 2 and self.atom(n).element == self.atom(m).element == 'C':
                adj[n].append(m)
                adj[m].append(n)

        if not adj:
            return [], []

        terminals = {x for x, y in adj.items() if len(y) == 1}
        cis_trans = []
        allene = []

        # structure of allene:
        # (first neighbor atom of enter atom, enter atom, exit atom, first neighbor atom of exit atom, central atom,
        #  second enter or None, second exit or None)

        # structure of cis_trans:
        # (first neighbor atom of enter atom, enter atom, exit atom, first neighbor atom of exit atom,
        #  first central atom, second central atom, second enter or None, second exit or None)

        while terminals:
            n = terminals.pop()
            m = adj[n][0]  # terminal atom has 1 neighbor always
            path = [n, m]
            while m not in terminals:
                n, m = m, next(x for x in adj[m] if x != n)
                path.append(m)
            terminals.discard(m)

            n, m = path[0], path[-1]
            if self.atom_total_h(n) == 2 or self.atom_total_h(m) == 2:
                continue  # ignore terminal alkenes
            nn = (x for x in self._adj[n] if x != path[1])
            mn = (x for x in self._adj[m] if x != path[-2])

            lp = len(path)
            if lp == 2:
                # ignore double bonds in small rings
                sp = set(path)
                if not any(True for ring in self.sssr if sp.issubset(ring) and len(ring) <= 7):
                    cis_trans.append((next(nn), n, m, next(mn), n, m, next(nn, None), next(mn, None)))
            elif lp % 2:
                allene.append((next(nn), n, m, next(mn), path[lp // 2], next(nn, None), next(mn, None)))
            else:
                cis_trans.append((next(nn), n, m, next(mn), path[lp // 2 - 1], path[lp // 2],
                                  next(nn, None), next(mn, None)))
        return cis_trans, allene

    @cached_property
    def __potentially_tetrahedron(self):
        # tetrahedral should be single bonded and contain zero or one H
        chiral = {}
        for n, m_bond in self._adj.items():
            if len(m_bond) < 3:
                continue
            if not all(x.order == 1 for x in m_bond.values()):
                continue
            if self.atom_total_h(n) > 1:  # more then one H impossible
                continue
            if self.atom_implicit_h(n) + len(m_bond) != 4:
                continue
            chiral[n] = tuple(m_bond)
        return chiral

    @cached_property
    def __potentially_atropisomer(self):
        if len(self.sssr) < 2:
            return []
        aromatic = [ring for ring in self.sssr if len(ring) in (5, 6) and self._adj[ring[0]][ring[-1]].order == 4
                    and all(self._adj[n][m].order == 4 for n, m in zip(ring, ring[1:]))]
        if len(aromatic) < 2:
            return []

        reduced_aromatic = [[x for x in x if len(self._adj[x]) == 3] for x in aromatic]  # remove :[CH]: atoms
        connections = {}
        for rings in combinations(range(len(reduced_aromatic)), 2):
            ring1, ring2 = rings
            for n, m in product(reduced_aromatic[ring1], reduced_aromatic[ring2]):
                if n in self._adj[m]:
                    if rings in connections:  # remove condensed rings or twice-bonded rings
                        del connections[rings]
                        break  # skip rings
                    connections[rings] = (n, m)

        # structure of atropisomer:
        # (first neighbor atom of ring1 atom, ring1 atom, ring2 atom, first neighbor atom of ring2 atom,
        #  second neighbor atom of ring1 atom, second neighbor atom of ring2 atom,
        #  nonring neighbor of first neighbor atom of ring1 atom or None,
        #  nonring neighbor of second neighbor atom of ring1 atom or None,
        #  nonring neighbor of first neighbor atom of ring2 atom or None,
        #  nonring neighbor of second neighbor atom of ring2 atom or None)

        atropos = []
        for (ring1, ring2), (n, m) in connections.items():
            r1n, r1m = (x for x in self._adj[n] if x != m)
            r2n, r2m = (x for x in self._adj[m] if x != n)

            nr1n = next((x for x in self._adj[r1n] if x not in aromatic[ring1]), None)
            nr1m = next((x for x in self._adj[r1m] if x not in aromatic[ring1]), None)
            nr2n = next((x for x in self._adj[r2n] if x not in aromatic[ring2]), None)
            nr2m = next((x for x in self._adj[r2m] if x not in aromatic[ring2]), None)

            # skip rings without substituents
            if nr1n is None and (nr1m is None or nr2n is None or nr2m is None):
                continue
            elif nr1m is None and (nr2n is None or nr2m is None):
                continue
            elif nr2n is nr2m:
                continue
            atropos.append((r1n, n, m, r2n, r1m, r2m, nr1n, nr1m, nr2n, nr2m))

        return atropos

    @cached_property
    def __potentially_plane(self):
        if not self.sssr:
            return []
        elif len(set(self.atom_order.values())) == len(self):
            return []
        not_aromatic = [ring for ring in self.sssr if any(self._adj[n][m].order != 4 for n, m in zip(ring, ring[1:]))]
        if not not_aromatic:
            return []



    def __tetrahedron(self):
        chiral = {}
        weights = self.atoms_order
        for n in self.__potentially_tetrahedron:
            m_bond = self._adj[n]
            # chiral atom all times contain unique neighbors
            if len(m_bond) == len({weights[x] for x in m_bond}):
                chiral[n] = tuple(m_bond)  # neighbors order
        """
        if chiral:  # generate new weights
            weights = weights.copy()
            countprime = iter(list(primes)[len(self):])
            for n in chiral:
                weights[n] = next(countprime)
            weights = self._morgan(weights)
            for n in self.__potentially_tetrahedron:
                if n in chiral:
                    continue
                m_bond = self._adj[n]
                if len(m_bond) == len({weights[x] for x in m_bond}):
                    chiral[n] = tuple(m_bond)  # neighbors order
        """
        return chiral


__all__ = ['Stereo']
