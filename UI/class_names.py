"""
class_names.py
----------------
The exact 260-class label list used by the trained model, in the same
sorted order the model's softmax output was trained on. Index 0 =
'Almonds 1', and np.argmax(predictions) maps directly into this list —
do not re-sort or re-order this list, it must match training time.
"""

import re
from collections import OrderedDict

CLASS_NAMES = [
    'Almonds 1', 'Apple 10', 'Apple 11', 'Apple 12', 'Apple 13', 'Apple 14',
    'Apple 17', 'Apple 18', 'Apple 19', 'Apple 20', 'Apple 21', 'Apple 22',
    'Apple 23', 'Apple 5', 'Apple 6', 'Apple 7', 'Apple 8', 'Apple 9',
    'Apple Braeburn 1', 'Apple Crimson Snow 1', 'Apple Golden 1', 'Apple Golden 2', 'Apple Golden 3', 'Apple Granny Smith 1',
    'Apple Pink Lady 1', 'Apple Red 1', 'Apple Red 2', 'Apple Red 3', 'Apple Red Delicious 1', 'Apple Red Yellow 1',
    'Apple Red Yellow 2', 'Apricot 1', 'Avocado 1', 'Avocado 2', 'Avocado Black 1', 'Avocado Black 2',
    'Avocado Green 1', 'Banana 1', 'Banana 3', 'Banana 4', 'Banana Lady Finger 1', 'Banana Red 1',
    'Bean pod 1', 'Beetroot 1', 'Blackberry 1', 'Blackberry 2', 'Blackberry 3', 'Blackberry 4',
    'Blackberry 5', 'Blueberry 1', 'Cabbage red 1', 'Cabbage white 1', 'Cactus fruit 1', 'Cactus fruit green 1',
    'Cactus fruit red 1', 'Caju seed 1', 'Cantaloupe 1', 'Cantaloupe 2', 'Cantaloupe 3', 'Carambola 1',
    'Carambola 2', 'Carambola 3', 'Carrot 1', 'Cauliflower 1', 'Celery 1', 'Cherimoya 1',
    'Cherry 1', 'Cherry 2', 'Cherry 3', 'Cherry 4', 'Cherry 5', 'Cherry Rainier 1',
    'Cherry Rainier 2', 'Cherry Rainier 3', 'Cherry Sour 1', 'Cherry Wax 1', 'Cherry Wax 2', 'Cherry Wax Black 1',
    'Cherry Wax Red 1', 'Cherry Wax Red 2', 'Cherry Wax Red 3', 'Cherry Wax Yellow 1', 'Chestnut 1', 'Clementine 1',
    'Cocos 1', 'Corn 1', 'Corn Husk 1', 'Cucumber 1', 'Cucumber 10', 'Cucumber 11',
    'Cucumber 12', 'Cucumber 13', 'Cucumber 3', 'Cucumber 4', 'Cucumber 5', 'Cucumber 6',
    'Cucumber 7', 'Cucumber 8', 'Cucumber 9', 'Dates 1', 'Dates 2', 'Eggplant 1',
    'Eggplant long 1', 'Fig 1', 'Ginger 2', 'Ginger Root 1', 'Gooseberry 1', 'Granadilla 1',
    'Grape 1', 'Grape Blue 1', 'Grape Pink 1', 'Grape White 1', 'Grape White 2', 'Grape White 3',
    'Grape White 4', 'Grape pink 2', 'Grapefruit Pink 1', 'Grapefruit White 1', 'Guava 1', 'Hazelnut 1',
    'Huckleberry 1', 'Kaki 1', 'Kiwi 1', 'Kohlrabi 1', 'Kumquats 1', 'Lemon 1',
    'Lemon Meyer 1', 'Limes 1', 'Lychee 1', 'Mandarine 1', 'Mango 1', 'Mango Red 1',
    'Mangostan 1', 'Maracuja 1', 'Melon Piel de Sapo 1', 'Mulberry 1', 'Nectarine 1', 'Nectarine Flat 1',
    'Nectarine Flat 2', 'Nut 1', 'Nut 2', 'Nut 3', 'Nut 4', 'Nut 5',
    'Nut Forest 1', 'Nut Pecan 1', 'Onion 2', 'Onion Red 1', 'Onion Red 2', 'Onion Red 3',
    'Onion White 1', 'Onion White 2', 'Orange 1', 'Orange 2', 'Orange 3', 'Orange peeled 1',
    'Papaya 1', 'Papaya 2', 'Passion Fruit 1', 'Peach 1', 'Peach 2', 'Peach 3',
    'Peach 4', 'Peach 5', 'Peach 6', 'Peach Flat 1', 'Peanut shell 1x 1', 'Pear 1',
    'Pear 10', 'Pear 11', 'Pear 12', 'Pear 13', 'Pear 14', 'Pear 2',
    'Pear 3', 'Pear 5', 'Pear 6', 'Pear 7', 'Pear 8', 'Pear 9',
    'Pear Abate 1', 'Pear Forelle 1', 'Pear Kaiser 1', 'Pear Monster 1', 'Pear Red 1', 'Pear Stone 1',
    'Pear Williams 1', 'Pepino 1', 'Pepper 1', 'Pepper 2', 'Pepper Green 1', 'Pepper Orange 1',
    'Pepper Orange 2', 'Pepper Red 1', 'Pepper Red 2', 'Pepper Red 3', 'Pepper Red 4', 'Pepper Red 5',
    'Pepper Yellow 1', 'Physalis 1', 'Physalis with Husk 1', 'Pineapple 1', 'Pineapple Mini 1', 'Pistachio 1',
    'Pitahaya Red 1', 'Plum 1', 'Plum 2', 'Plum 3', 'Plum 4', 'Plum 5',
    'Pomegranate 1', 'Pomelo Sweetie 1', 'Potato Red 1', 'Potato Red 2', 'Potato Sweet 1', 'Potato White 1',
    'Quince 1', 'Quince 2', 'Quince 3', 'Quince 4', 'Rambutan 1', 'Raspberry 1',
    'Raspberry 2', 'Raspberry 3', 'Raspberry 4', 'Raspberry 5', 'Raspberry 6', 'Redcurrant 1',
    'Salak 1', 'Strawberry 1', 'Strawberry 2', 'Strawberry 3', 'Strawberry Wedge 1', 'Tamarillo 1',
    'Tangelo 1', 'Tomato 1', 'Tomato 10', 'Tomato 11', 'Tomato 2', 'Tomato 3',
    'Tomato 4', 'Tomato 5', 'Tomato 7', 'Tomato 8', 'Tomato 9', 'Tomato Cherry Maroon 1',
    'Tomato Cherry Orange 1', 'Tomato Cherry Red 1', 'Tomato Cherry Red 2', 'Tomato Cherry Yellow 1', 'Tomato Heart 1', 'Tomato Maroon 1',
    'Tomato Maroon 2', 'Tomato Yellow 1', 'Walnut 1', 'Watermelon 1', 'Zucchini 1', 'Zucchini Green 1',
    'Zucchini dark 1', 'orange 4',
]

assert len(CLASS_NAMES) == 260, f"Expected 260 classes, got {len(CLASS_NAMES)}"


def display_name(raw_label: str) -> str:
    """Strip a trailing variant number, e.g. 'Apple Red Delicious 1' -> 'Apple Red Delicious'.
    Falls back to the raw label if there's no trailing number to strip."""
    cleaned = re.sub(r'\s+\d+x?\s*\d*$', '', raw_label).strip()
    return cleaned if cleaned else raw_label


def base_category(raw_label: str) -> str:
    """First word of the display name, used to group variants into a showcase grid
    (e.g. all 'Apple ...' classes bucket under 'Apple')."""
    name = display_name(raw_label)
    return name.split(' ')[0].capitalize()


def grouped_classes() -> "OrderedDict[str, list]":
    """Returns {base_category: [display_name, ...]} preserving first-seen order,
    with de-duplicated display names per category (variant numbers stripped)."""
    groups: "OrderedDict[str, list]" = OrderedDict()
    for raw in CLASS_NAMES:
        cat = base_category(raw)
        name = display_name(raw)
        groups.setdefault(cat, [])
        if name not in groups[cat]:
            groups[cat].append(name)
    return groups
