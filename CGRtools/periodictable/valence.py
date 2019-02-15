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


# elements, [charge, [bonds, [implicitH]]]
_valence_rules = (
    (('Li', 'Na', 'K', 'Rb', 'Cs', 'Fr'),),
    (('H', 'Li', 'Na', 'K', 'Rb', 'Cs', 'Fr'), 0, 1),
    (('H', 'Li', 'Na', 'K', 'Rb', 'Cs', 'Fr'), 1),

    (('Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra'),),
    (('Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra'), 0, 2),
    (('Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra'), 1, 1),
    (('Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra'), 2),

    ('B', -2, 3, 3),
    (('B', 'Al', 'Ga', 'In', 'Tl'), -1, 4, 4),
    (('Al', 'Ga', 'In', 'Tl'),),
    ('B', 0, 3, 3),
    (('Al', 'Ga', 'In', 'Tl'), 0, 3, 2),
    ('B', 1, 2, 2),
    (('Al', 'Ga', 'In', 'Tl'), 1),
    (('Al', 'Ga', 'In', 'Tl'), 1, 2, 1),
    ('B', 2, 1, 1),
    (('Al', 'Ga', 'In', 'Tl'), 2, 1),
    (('B', 'Al', 'Ga', 'In', 'Tl'), 3),

    (('C', 'Si', 'Ge'), -2, 2, 2),
    (('C', 'Si', 'Ge'), -1, 3, 3),
    (('Sn', 'Pb'),),
    ('Pb', 0, 2, 1),
    (('C', 'Si', 'Ge'), 0, 4, 4),
    ('Sn', 0, 4, 3),
    ('Pb', 0, 4, 1),
    (('Sn', 'Pb'), 0, 5),
    (('Sn', 'Pb'), 0, 6),
    (('C', 'Si', 'Ge', 'Sn'), 1, 3, 3),
    ('Pb', 1, 1, 1),
    ('Pb', 1, 3, 1),
    ('Pb', 1, 4),
    (('Sn', 'Pb'), 1, 5),
    (('Sn', 'Pb'), 2),
    (('C', 'Si', 'Ge'), 2, 2, 2),
    (('Sn', 'Pb'), 2, 2, 1),
    (('Ge', 'Sn', 'Pb'), 3, 1, 1),
    ('Pb', 3, 2),
    ('Pb', 3, 3),

    (('N', 'P', 'As', 'Sb', 'Bi'), -3),
    (('N', 'P', 'As', 'Sb', 'Bi'), -2, 1, 1),
    (('N', 'P', 'As', 'Sb', 'Bi'), -1, 2, 2),
    (('P', 'As', 'Sb', 'Bi'), -1, 4),
    ('Bi',),
    ('Bi', 0, 3, 2),
    (('N', 'P', 'As', 'Sb'), 0, 3, 3),
    (('P', 'As', 'Sb', 'Bi'), 0, 5, 1),
    (('N', 'P', 'As', 'Sb', 'Bi'), 1, 4, 4),
    (('N', 'P', 'As', 'Sb', 'Bi'), 2, 3, 3),

    (('O', 'S', 'Se', 'Te', 'Po'), -2),
    (('O', 'S', 'Se', 'Te', 'Po'), -1, 1, 1),
    (('O', 'S', 'Se', 'Te', 'Po'), 0, 2, 2),
    (('S', 'Se', 'Te', 'Po'), 0, 4),
    (('S', 'Se', 'Te', 'Po'), 0, 6, 1),
    (('O', 'S', 'Se', 'Te', 'Po'), 1, 3, 3),
    (('S', 'Se', 'Te', 'Po'), 1, 5, 1),
    (('Se', 'Te', 'Po'), 1, 1, 1),

    (('F', 'Cl', 'Br', 'I', 'At'), 0, 1, 1),
    (('F', 'Cl', 'Br', 'I', 'At'), 1, 2, 2),
    (('F', 'Cl', 'Br', 'I', 'At'), -1),

    (('He', 'Ne', 'Ar', 'Kr', 'Xe', 'Rn'),),

    (('Sc',), -3),
    (('Sc',), -3, 1),
)
