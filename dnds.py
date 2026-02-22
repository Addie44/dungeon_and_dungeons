"""
╔════════════════════════════════════════╗
║         THE FORGOTTEN DUNGEON          ║
║      A Text-Based Adventure Game       ║
║             By: Adi Arjmnd             ║
╚════════════════════════════════════════╝

Navigate the dungeon, fight monsters, collect loot, and find the exit!
"""

import random
import time
import sys
import os

RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

def clr(text, color): return f"{color}{text}{RESET}"

def slow_print(text, delay=0.025):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def hr():  print(clr("─" * 54, CYAN))
def hr2(): print(clr("═" * 54, YELLOW))

def pause(msg="  [Press Enter to continue...]"):
    input(clr(msg, CYAN))

#FIX: CHANGE "IRON SWORD"/"PLATE ARMOR" => VALUES
ITEMS = {
    "Health Potion":         {"type": "consumable", "effect": "heal",     "value": 30,   "desc": "Restores 30 HP"},
    "Greater Health Potion": {"type": "consumable", "effect": "heal",     "value": 60,   "desc": "Restores 60 HP"},
    "Antidote":              {"type": "consumable", "effect": "antidote", "value": 0,    "desc": "Cures poison"},
    "Iron Sword":            {"type": "weapon",     "effect": "damage",   "value": 8,    "desc": "+8 attack"},
    "Steel Sword":           {"type": "weapon",     "effect": "damage",   "value": 14,   "desc": "+14 attack"},
    "Shadow Dagger":         {"type": "weapon",     "effect": "damage",   "value": 11,   "desc": "+11 attack, high crit chance"},
    "Cursed Blade":          {"type": "weapon",     "effect": "damage",   "value": 20,   "desc": "+20 attack, but drains 3 HP/room"},
    "Leather Armor":         {"type": "armor",      "effect": "defense",  "value": 4,    "desc": "+4 defense"},
    "Chain Mail":            {"type": "armor",      "effect": "defense",  "value": 8,    "desc": "+8 defense"},
    "Plate Armor":           {"type": "armor",      "effect": "defense",  "value": 14,   "desc": "+14 defense"},
    "Gold Coin":             {"type": "treasure",   "effect": "gold",     "value": 20,   "desc": "Worth 20 gold"},
    "Elixir of Power":       {"type": "consumable", "effect": "attack",   "value": 5,    "desc": "+5 attack permanently"},
    "Rage Potion":           {"type": "consumable", "effect": "attack",   "value": 8,    "desc": "+8 attack permanently"},
    "Smoke Bomb":            {"type": "consumable", "effect": "flee",     "value": 1,    "desc": "Guarantees escape from combat"},
    "Ancient Key":           {"type": "consumable", "effect": "key",      "value": 50,   "desc": "Unlocks a hidden vault (+50g)"},  # added
    "Angelic Addie's Sword": {"type": "weapon",     "effect": "damage",   "value": 9999, "desc": "⚡ Two-Handed Divine Blade — instantly slays any foe"},
}

#NOTE: ABOVE ROOM 5 ITEMS
LATE_ITEMS = {"Cursed Blade", "Plate Armor", "Steel Sword", "Ancient Key"}  # added

MONSTERS = [
    {"name": "Goblin Scout",     "hp": 25,  "attack": 7,  "defense": 1,  "xp": 15,  "gold": 5,  "loot": "Gold Coin",            "ability": None},
    {"name": "Skeleton",         "hp": 40,  "attack": 10, "defense": 4,  "xp": 25,  "gold": 8,  "loot": "Health Potion",         "ability": None},
    {"name": "Venomfang Spider", "hp": 30,  "attack": 9,  "defense": 2,  "xp": 30,  "gold": 10, "loot": "Antidote",              "ability": "poison"},
    {"name": "Orc Warrior",      "hp": 60,  "attack": 15, "defense": 7,  "xp": 45,  "gold": 18, "loot": "Iron Sword",            "ability": None},
    {"name": "Dark Wizard",      "hp": 45,  "attack": 20, "defense": 3,  "xp": 55,  "gold": 22, "loot": "Elixir of Power",       "ability": "magic_bolt"},
    {"name": "Werewolf",         "hp": 70,  "attack": 18, "defense": 6,  "xp": 65,  "gold": 25, "loot": "Greater Health Potion", "ability": "rend"},
    {"name": "Stone Golem",      "hp": 100, "attack": 22, "defense": 14, "xp": 90,  "gold": 35, "loot": "Chain Mail",            "ability": None},
    {"name": "Vampire Lord",     "hp": 85,  "attack": 25, "defense": 8,  "xp": 110, "gold": 45, "loot": "Shadow Dagger",         "ability": "lifesteal"},
    {"name": "Lich King",        "hp": 110, "attack": 28, "defense": 10, "xp": 140, "gold": 55, "loot": "Plate Armor",           "ability": "curse"},
    {"name": "Ancient Dragon",   "hp": 160, "attack": 35, "defense": 16, "xp": 200, "gold": 80, "loot": "Steel Sword",           "ability": "breathe_fire"},
]


ROOMS = [
    {
        "name": "Dimly Lit Corridor",
        "desc": "A long, narrow passage. Torches flicker weakly on the walls.",
        "encounters": [
            ["look_around", "monster", "trap"],
            ["monster", "look_around", "item"],
            ["trap", "monster", "look_around"],
        ],
    },
    {
        "name": "Ancient Chamber",
        "desc": "Crumbling stone pillars line the walls. Moss covers everything.",
        "encounters": [
            ["look_around", "puzzle", "monster", "item"],
            ["monster", "look_around", "item", "puzzle"],
            ["look_around", "item", "monster", "empty"],
        ],
    },
    {
        "name": "Treasure Vault",
        "desc": "Gold glimmers in the darkness — but something moves between the chests.",
        "encounters": [
            ["item", "mimic", "look_around", "item"],
            ["look_around", "item", "monster", "item"],
            ["mimic", "look_around", "item", "item"],
        ],
    },
    {
        "name": "Monster Den",
        "desc": "Bones crunch beneath your boots. The stench of death is overwhelming.",
        "encounters": [
            ["ambush", "monster", "look_around", "monster"],
            ["monster", "ambush", "look_around", "item"],
            ["ambush", "look_around", "monster", "monster"],
        ],
    },
    {
        "name": "Collapsed Hallway",
        "desc": "Rubble blocks most of the path. You squeeze through narrow gaps.",
        "encounters": [
            ["trap", "look_around", "trap", "item"],
            ["look_around", "trap", "monster", "empty"],
            ["trap", "monster", "look_around", "trap"],
        ],
    },
    {
        "name": "Misty Crypt",
        "desc": "Cold fog drifts at knee height. Ghostly whispers fill the air.",
        "encounters": [
            ["look_around", "curse_room", "monster", "item"],
            ["curse_room", "look_around", "monster", "puzzle"],
            ["monster", "look_around", "curse_room", "item"],
        ],
    },
    {
        "name": "Flooded Chamber",
        "desc": "Dark water covers the floor to your waist. The ceiling drips.",
        "encounters": [
            ["drain_event", "look_around", "monster", "item"],
            ["look_around", "drain_event", "trap", "item"],
            ["monster", "drain_event", "look_around", "item"],
        ],
    },
    {
        "name": "Cursed Shrine Room",
        "desc": "A blood-stained altar pulses with dark energy. Eyes watch from the shadows.",
        "encounters": [
            ["look_around", "curse_room", "monster", "curse_room"],
            ["curse_room", "look_around", "ambush", "item"],
            ["monster", "curse_room", "look_around", "puzzle"],
        ],
    },
    {
        "name": "Goblin War Camp",
        "desc": "Crude tents and campfires fill the room. Goblins scramble for weapons!",
        "encounters": [
            ["ambush", "monster", "look_around", "monster", "item"],
            ["monster", "ambush", "look_around", "item", "monster"],
            ["ambush", "look_around", "monster", "item", "ambush"],
        ],
    },
    {
        "name": "Hall of Echoes",
        "desc": "Every footstep rings out impossibly loud. The walls seem to shift.",
        "encounters": [
            ["echo_challenge", "look_around", "monster", "item"],
            ["look_around", "echo_challenge", "trap", "item"],
            ["monster", "look_around", "echo_challenge", "item"],
        ],
    },
    {
        "name": "The Bone Pit",
        "desc": "You peer down into a deep pit — then realise you're already inside it.",
        "encounters": [
            ["trap", "ambush", "look_around", "monster"],
            ["ambush", "trap", "look_around", "item"],
            ["trap", "monster", "ambush", "look_around"],
        ],
    },
    {
        "name": "Arcane Library",
        "desc": "Shelves of ancient tomes line the walls. Some of them are moving.",
        "encounters": [
            ["look_around", "puzzle", "item", "monster"],
            ["puzzle", "look_around", "item", "puzzle"],
            ["look_around", "item", "puzzle", "monster"],
        ],
    },
]

#NOTE: ADDIE => THE HP IS 90 JUST TO MAKE THE HEALTH BAR LOOK BETTER WITH THE CURRENT ITEMS/MONSTERS. CAN BE CHANGED LATER IF NEEDED
class Player:
    def __init__(self, name):
        self.name          = name
        self.hp            = 90
        self.max_hp        = 90
        self.attack        = 8
        self.defense       = 1
        self.level         = 1
        self.xp            = 0
        self.xp_next       = 120
        self.gold          = 0
        self.inventory     = []
        self.weapon        = None
        self.armor         = None
        self.rooms_cleared = 0
        self.poisoned      = False
        self.poison_turns  = 0
        self.cursed        = False
        self.kills         = 0

    def status(self):
        hr()
        bar_len = 22
        filled  = max(0, int((self.hp / self.max_hp) * bar_len))  # fix: clamp to 0 so bar never goes negative
        hp_col  = GREEN if self.hp > self.max_hp * 0.5 else (YELLOW if self.hp > self.max_hp * 0.25 else RED)
        bar     = clr("█" * filled, hp_col) + clr("░" * (bar_len - filled), RED)
        tags    = ""
        if self.poisoned: tags += clr(" [POISONED]", MAGENTA)  # fix: was GREEN, confusing with HP bar
        if self.cursed:   tags += clr(" [CURSED]",   MAGENTA)
        print(f"  {clr(self.name, BOLD)} | Lv.{self.level} | [{bar}] {self.hp}/{self.max_hp}{tags}")
        print(f"  ATK:{self.total_attack()}  DEF:{self.total_defense()}  XP:{self.xp}/{self.xp_next}  Gold:{self.gold}g  Kills:{self.kills}")
        print(f"  ⚔  {self.weapon or 'Bare Hands'}   🛡  {self.armor or 'No Armor'}")
        hr()

    def total_attack(self):
        b = ITEMS[self.weapon]["value"] if self.weapon else 0
        return self.attack + b + (-3 if self.cursed else 0)

    def total_defense(self):
        b = ITEMS[self.armor]["value"] if self.armor else 0
        return max(0, self.defense + b + (-2 if self.cursed else 0))

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_next:
            self.level_up()

    def level_up(self):
        self.level   += 1
        self.xp      -= self.xp_next
        self.xp_next  = int(self.xp_next * 1.6)
        self.max_hp  += 15
        self.hp       = min(self.hp + 30, self.max_hp)
        self.attack  += 2
        self.defense += 1
        slow_print(clr(f"\n  ✨ LEVEL UP → Lv.{self.level}! HP+30 restored, stats increased!", YELLOW))

    def tick_status(self):
        """Returns True if the player died this tick."""
        if self.poisoned:
            dmg = random.randint(4, 10)
            self.hp -= dmg
            slow_print(clr(f"  ☠  Poison burns through you! -{dmg} HP", MAGENTA))  # fix: use MAGENTA for poison
            self.poison_turns -= 1
            if self.poison_turns <= 0:
                self.poisoned = False
                slow_print(clr("  The poison finally fades.", YELLOW))
        if self.weapon == "Cursed Blade":
            self.hp -= 3
            slow_print(clr("  💀 The Cursed Blade drains your life... -3 HP", MAGENTA))
        return self.hp <= 0  # fix: caller can now check if player died

    def show_inventory(self):
        if not self.inventory:
            print(clr("  Your inventory is empty.", YELLOW)); return False
        print(clr("\n  📦 Inventory:", BOLD))
        for i, itm in enumerate(self.inventory, 1):
            tag = ""
            if itm == self.weapon: tag = clr(" [equipped]", GREEN)
            elif itm == self.armor: tag = clr(" [equipped]", GREEN)
            print(f"    {i}. {itm} — {ITEMS[itm]['desc']}{tag}")  # fix: show equipped status
        return True

    def use_item(self):
        consumables = [i for i in self.inventory if ITEMS[i]["type"] == "consumable"]
        if not consumables:
            print(clr("  No usable items!", YELLOW)); return None
        print(clr("\n  🧪 Use which item?", BOLD))
        for i, itm in enumerate(consumables, 1):
            print(f"    {i}. {itm} — {ITEMS[itm]['desc']}")  # fix: show item desc in menu
        print("    0. Cancel")
        pick = input("  > ").strip()
        if pick == "0" or not pick.isdigit(): return None
        pick = int(pick)
        if not (1 <= pick <= len(consumables)): return None
        itm    = consumables[pick - 1]
        effect = ITEMS[itm]["effect"]
        value  = ITEMS[itm]["value"]
        self.inventory.remove(itm)
        if effect == "heal":
            healed = min(value, self.max_hp - self.hp)
            self.hp += healed
            slow_print(clr(f"  💊 {itm}: +{healed} HP restored. ({self.hp}/{self.max_hp})", GREEN))
        elif effect == "attack":
            self.attack += value
            slow_print(clr(f"  ⚡ {itm}: Attack permanently +{value}!", YELLOW))
        elif effect == "antidote":
            if self.poisoned:
                self.poisoned = False; self.poison_turns = 0
                slow_print(clr("  💚 Antidote taken. Poison cured!", GREEN))
            else:
                self.inventory.append(itm)  # fix: refund antidote if not poisoned
                slow_print(clr("  You're not poisoned! Antidote returned.", YELLOW))
        elif effect == "flee":
            return "smoke_bomb"
        elif effect == "key":
            self.gold += value  # fix: Ancient Key now actually does something (+50g)
            slow_print(clr(f"  🔑 The key opens a hidden vault! +{value}g!", YELLOW))
        return None

    def equip_item(self, itm):
        itype = ITEMS[itm]["type"]
        if itype == "weapon":
            if self.weapon: self.inventory.append(self.weapon)
            self.weapon = itm
            self.inventory.remove(itm)
            slow_print(clr(f"  ⚔  Equipped {itm}!", GREEN))
            if itm == "Cursed Blade":
                slow_print(clr("  ⚠  WARNING: Cursed Blade drains 3 HP every room!", RED))
        elif itype == "armor":
            if self.armor: self.inventory.append(self.armor)
            self.armor = itm
            self.inventory.remove(itm)
            slow_print(clr(f"  🛡  Equipped {itm}!", GREEN))


# ─── Inventory Menu (shared between combat and exploration) ───────────────────
# Added: unified menu replaces separate show_inventory + use_item calls
def inventory_menu(player):
    """Show inventory + optionally use or equip an item. Returns 'smoke_bomb' or None."""
    has_items = player.show_inventory()
    if not has_items:
        return None
    print(clr("\n  [1] Use consumable   [2] Equip gear   [0] Cancel", BOLD))
    act = input("  > ").strip()
    if act == "1":
        return player.use_item()
    elif act == "2":
        gear = [i for i in player.inventory
                if ITEMS[i]["type"] in ("weapon", "armor")
                and i != player.weapon and i != player.armor]
        if not gear:
            print(clr("  No unequipped gear in inventory.", YELLOW))
            return None
        print(clr("\n  Equip which?", BOLD))
        for i, g in enumerate(gear, 1):
            print(f"    {i}. {g} — {ITEMS[g]['desc']}")
        print("    0. Cancel")
        pick = input("  > ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(gear):
            player.equip_item(gear[int(pick) - 1])
    return None

# ─── Combat ──────────────────────────────────────────────────────────────────
def combat(player, monster_template, ambush=False):
    monster = dict(monster_template)
    monster["max_hp"] = monster["hp"]

    if ambush:
        slow_print(clr(f"\n  💥 AMBUSH! The {monster['name']} leaps at you!", RED))
        hit = max(1, monster["attack"] - player.total_defense() + random.randint(0, 6))
        player.hp -= hit
        slow_print(clr(f"  You take {hit} surprise damage!", RED))
        time.sleep(0.5)
    else:
        slow_print(clr(f"\n  ⚔  A {monster['name']} blocks your path!", RED))
        time.sleep(0.3)

    smoke_used = False

    while player.hp > 0 and monster["hp"] > 0:
        m_pct = monster["hp"] / monster["max_hp"]
        m_bar = clr("█" * int(m_pct * 16), RED) + clr("░" * (16 - int(m_pct * 16)), YELLOW)
        print(clr(f"\n  ► {monster['name']}  [{m_bar}]  {monster['hp']}/{monster['max_hp']} HP", RED))
        p_col = GREEN if player.hp > player.max_hp * 0.5 else (YELLOW if player.hp > player.max_hp * 0.25 else RED)
        print(f"  ► You          HP: {clr(str(player.hp), p_col)}/{player.max_hp}")
        if player.poisoned: print(clr(f"  ☠ Poisoned ({player.poison_turns} turns left)", GREEN))
        print(clr("\n  [1] Attack   [2] Use Item   [3] Flee", BOLD))
        choice = input("  > ").strip()

        if choice == "1":
            if player.weapon == "Angelic Addie's Sword":
                slow_print(clr("\n  ✨ The blade blazes with holy fire...", YELLOW))
                time.sleep(0.5)
                slow_print(clr(f"  ☀  DIVINE WRATH obliterates the {monster['name']}!", YELLOW))
                monster["hp"] = 0
            else:
                crit_chance = 0.25 if player.weapon == "Shadow Dagger" else 0.10
                is_crit = random.random() < crit_chance
                dmg = max(1, player.total_attack() - monster["defense"] + random.randint(-3, 5))
                if is_crit:
                    dmg = int(dmg * 1.8)
                    slow_print(clr(f"  💥 CRITICAL HIT! You deal {dmg} damage!", YELLOW))
                else:
                    slow_print(clr(f"  You deal {dmg} damage to the {monster['name']}!", GREEN))
                monster["hp"] -= dmg

            if monster["hp"] <= 0:
                slow_print(clr(f"\n  ☠  {monster['name']} defeated!", YELLOW))
                player.kills += 1
                player.gain_xp(monster["xp"])
                player.gold += monster["gold"]
                print(clr(f"  +{monster['xp']} XP  +{monster['gold']}g", YELLOW))
                loot = monster.get("loot")
                if loot and loot in ITEMS and random.random() < 0.50:
                    player.inventory.append(loot)
                    slow_print(clr(f"  🎁 Dropped: {loot}!", CYAN))
                    if ITEMS[loot]["type"] in ("weapon", "armor"):
                        eq = input(clr(f"  Equip {loot}? (y/n): ", BOLD)).strip().lower()
                        if eq == "y": player.equip_item(loot)
                return True

            #NOTE: IF YOU WANT T ADD MORE ABILITIES THIS S THE PLACE TO DO IT JUST COPY THE ELIF BLOCKS AND CHANGE THE CONDITIONS/OUTCOMES AS NEEDED
            ability    = monster.get("ability")
            enemy_dmg  = 0

            if ability == "poison" and not player.poisoned and random.random() < 0.40:
                slow_print(clr(f"  🕷  {monster['name']} injects venom! POISONED!", MAGENTA))  # fix: use MAGENTA for poison
                player.poisoned = True
                player.poison_turns = random.randint(3, 5)
                enemy_dmg = max(1, monster["attack"] // 2 - player.total_defense())

            elif ability == "magic_bolt" and random.random() < 0.35:
                enemy_dmg = max(1, monster["attack"] + random.randint(4, 10))
                slow_print(clr(f"  🔮 Magic bolt! Bypasses armor! -{enemy_dmg} HP!", MAGENTA))
                player.hp -= enemy_dmg
                enemy_dmg = 0

            elif ability == "lifesteal" and random.random() < 0.30:
                enemy_dmg = max(1, monster["attack"] - player.total_defense() + random.randint(-2, 4))
                heal_amt  = enemy_dmg // 2
                monster["hp"] = min(monster["max_hp"], monster["hp"] + heal_amt)
                slow_print(clr(f"  🩸 {monster['name']} drains your life for {enemy_dmg}! Heals {heal_amt} HP!", MAGENTA))
                player.hp -= enemy_dmg  # fix: was healed monster but never damaged player
                enemy_dmg = 0

            elif ability == "rend" and random.random() < 0.30:
                enemy_dmg = max(1, monster["attack"] - player.total_defense() + random.randint(5, 12))
                slow_print(clr(f"  🐺 REND! Savage strike for {enemy_dmg}!", RED))

            elif ability == "curse" and not player.cursed and random.random() < 0.25:
                player.cursed = True
                slow_print(clr(f"  💀 You are CURSED! ATK-3 DEF-2!", MAGENTA))
                enemy_dmg = max(1, monster["attack"] - player.total_defense())

            elif ability == "breathe_fire" and random.random() < 0.40:
                enemy_dmg = max(1, monster["attack"] + random.randint(8, 18))
                slow_print(clr(f"  🔥 FIRE BREATH! -{enemy_dmg} HP!", RED))
                player.hp -= enemy_dmg
                enemy_dmg = 0

            else:
                enemy_dmg = max(1, monster["attack"] - player.total_defense() + random.randint(-3, 4))
                slow_print(clr(f"  {monster['name']} hits you for {enemy_dmg}!", RED))

            if enemy_dmg > 0:
                player.hp -= enemy_dmg

            if player.poisoned:
                p_dmg = random.randint(2, 5)
                player.hp -= p_dmg
                slow_print(clr(f"  ☠  Poison: -{p_dmg} HP", MAGENTA))  # fix: match poison colour theme

        elif choice == "2":
            result = player.use_item()
            if result == "smoke_bomb":
                smoke_used = True
                break

        elif choice == "3":
            if random.random() < 0.35:
                slow_print(clr("  You slip away into the shadows!", YELLOW))
                return False
            else:
                fd = max(1, (monster["attack"] - player.total_defense()) // 2 + random.randint(1, 6))  # fix: was monster["attack"] - (defense//2) due to precedence
                player.hp -= fd
                slow_print(clr(f"  Caught fleeing! -{fd} HP!", RED))
        else:
            print(clr("  Invalid choice.", RED))

    if smoke_used:
        slow_print(clr("  💨 You vanish in a cloud of smoke!", YELLOW))
        return False

    return player.hp > 0

def ev_monster(player, room_num):
    tier       = min(room_num, len(MONSTERS))
    candidates = MONSTERS[max(0, tier - 4):tier]
    combat(player, random.choice(candidates))

def ev_ambush(player, room_num):
    tier       = min(room_num, len(MONSTERS))
    candidates = MONSTERS[max(0, tier - 3):tier]
    combat(player, random.choice(candidates), ambush=True)

def ev_mimic(player, room_num):
    slow_print(clr("\n  📦 A chest sits in the corner, lid slightly ajar...", CYAN))
    time.sleep(0.8)
    choice = input(clr("  Open it? (y/n): ", BOLD)).strip().lower()
    if choice == "y":
        slow_print(clr("  It has TEETH! A Mimic lunges at you!", RED))
        mimic = {"name": "Mimic", "hp": 55, "attack": 18, "defense": 5,
                 "xp": 70, "gold": 40, "loot": "Greater Health Potion", "ability": None}
        combat(player, mimic, ambush=True)
    else:
        slow_print(clr("  You back away slowly. Smart move.", YELLOW))

def ev_item(player, room_num):
    pool = [k for k in ITEMS
            if k != "Angelic Addie's Sword"
            and not (k in LATE_ITEMS and room_num < 5)]  # fix: late-game items blocked in early rooms
    itm  = random.choice(pool)
    slow_print(clr(f"\n  ✨ You find something: {clr(itm, BOLD)} ({ITEMS[itm]['desc']})", CYAN))
    player.inventory.append(itm)
    if ITEMS[itm]["type"] == "treasure":
        player.gold += ITEMS[itm]["value"]
        player.inventory.remove(itm)
        slow_print(clr(f"  +{ITEMS[itm]['value']}g added to your purse.", YELLOW))
    elif ITEMS[itm]["type"] in ("weapon", "armor"):
        eq = input(clr(f"  Equip {itm}? (y/n): ", BOLD)).strip().lower()
        if eq == "y": player.equip_item(itm)

def ev_trap(player, room_num):
    traps = ["spike", "poison_dart", "collapse", "fire_vent", "electric_floor", "cursed_rune"]
    t = random.choice(traps)
    dodge = random.random() < 0.20

    if t == "spike":
        slow_print(clr("\n  ⚠  You step on a pressure plate...", YELLOW))
        time.sleep(0.6)
        if dodge:
            slow_print(clr("  You leap back just in time! Spikes graze you for 5 damage.", YELLOW))
            player.hp -= 5
        else:
            dmg = random.randint(15, 28)
            player.hp -= dmg
            slow_print(clr(f"  💥 SPIKE TRAP! You are skewered for {dmg} damage!", RED))

    elif t == "poison_dart":
        slow_print(clr("\n  💉 A dart flies from a hidden hole in the wall!", YELLOW))
        if dodge:
            slow_print(clr("  You duck! It misses by inches.", YELLOW))
        else:
            dmg = random.randint(5, 12)
            player.hp -= dmg
            player.poisoned = True
            player.poison_turns = random.randint(3, 6)
            slow_print(clr(f"  The dart hits! {dmg} damage + POISONED!", RED))

    elif t == "collapse":
        slow_print(clr("\n  🪨 The ceiling groans ominously...", YELLOW))
        time.sleep(0.5)
        if dodge:
            slow_print(clr("  You sprint forward as rubble crashes behind you! Safe!", YELLOW))
        else:
            dmg = random.randint(18, 35)
            player.hp -= dmg
            slow_print(clr(f"  💥 CEILING COLLAPSE! -{dmg} HP!", RED))

    elif t == "fire_vent":
        slow_print(clr("\n  🔥 You smell sulphur a split second too late...", YELLOW))
        if dodge:
            slow_print(clr("  You dive to the side! Just 4 damage from the heat.", YELLOW))  # fix: message said dodged but still did 8 damage
            player.hp -= 4
        else:
            dmg = random.randint(18, 30)
            player.hp -= dmg
            slow_print(clr(f"  🔥 FIRE VENT! You are scorched for {dmg} damage!", RED))

    elif t == "electric_floor":
        slow_print(clr("\n  ⚡ The floor tiles shimmer with strange energy...", YELLOW))
        time.sleep(0.5)
        if dodge:
            slow_print(clr("  You hop between safe tiles! Only 6 damage.", YELLOW))
            player.hp -= 6
        else:
            dmg = random.randint(12, 24)
            player.hp -= dmg
            slow_print(clr(f"  ⚡ ELECTRIC SHOCK! Muscles seize! -{dmg} HP!", RED))

    elif t == "cursed_rune":
        slow_print(clr("\n  💀 You accidentally read a glowing rune on the floor...", MAGENTA))
        if not player.cursed:
            player.cursed = True
            slow_print(clr("  Your vision darkens. You are CURSED! (ATK-3, DEF-2)", MAGENTA))
        else:
            dmg = random.randint(10, 20)
            player.hp -= dmg
            slow_print(clr(f"  The rune explodes! Already cursed — it just hurts instead. -{dmg} HP", MAGENTA))

def ev_puzzle(player, room_num):
    slow_print(clr("\n  🧩 A glowing inscription blocks the passage:", CYAN))
    time.sleep(0.4)
    puzzles = [
        {"q": "  'I speak without a mouth and hear without ears.\n   I have no body, but come alive with wind. What am I?'",
         "a": "echo", "reward": "Greater Health Potion"},
        {"q": "  'The more you take, the more you leave behind. What am I?'",
         "a": "footsteps", "reward": "Elixir of Power"},
        {"q": "  'I have cities but no houses, mountains but no trees,\n   water but no fish. What am I?'",
         "a": "map", "reward": "Plate Armor"},
        {"q": "  'What has hands but cannot clap?'",
         "a": "clock", "reward": "Rage Potion"},
        {"q": "  'I am always in front of you but cannot be seen. What am I?'",
         "a": "future", "reward": "Smoke Bomb"},
        {"q": "  'What can run but never walks, has a mouth but never talks,\n   has a head but never weeps, has a bed but never sleeps?'",
         "a": "river", "reward": "Chain Mail"},
        {"q": "  'I have teeth but cannot bite. I open things with great delight. What am I?'",
         "a": "key", "reward": "Antidote"},
    ]
    p = random.choice(puzzles)
    slow_print(p["q"])
    ans = input(clr("\n  Your answer: ", BOLD)).strip().lower()
    if ans == p["a"]:
        slow_print(clr(f"  ✅ Correct! A hidden panel slides open — you find: {p['reward']}!", GREEN))
        player.inventory.append(p["reward"])
        if ITEMS[p["reward"]]["type"] in ("weapon", "armor"):
            eq = input(clr(f"  Equip {p['reward']}? (y/n): ", BOLD)).strip().lower()
            if eq == "y": player.equip_item(p["reward"])
    else:
        dmg = random.randint(15, 25)
        player.hp -= dmg
        slow_print(clr(f"  ❌ Wrong! The floor gives way! -{dmg} HP!", RED))
        slow_print(clr(f"  (The answer was: {p['a']})", YELLOW))

def ev_curse_room(player, room_num):
    slow_print(clr("\n  💀 A suffocating dark energy fills this corner of the room...", MAGENTA))
    time.sleep(0.5)
    outcomes = ["curse", "drain_gold", "drain_hp", "drain_xp", "nothing"]
    outcome  = random.choice(outcomes)
    if outcome == "curse":
        if not player.cursed:
            player.cursed = True
            slow_print(clr("  Dark voices chant your name. You are CURSED! (ATK-3, DEF-2)", MAGENTA))
        else:
            dmg = random.randint(8, 18)
            player.hp -= dmg
            slow_print(clr(f"  Already cursed — the darkness just hurts instead. -{dmg} HP", MAGENTA))
    elif outcome == "drain_gold":
        stolen = min(player.gold, random.randint(10, 35))
        player.gold -= stolen
        slow_print(clr(f"  Spectral hands plunge into your purse and steal {stolen}g!", MAGENTA))
    elif outcome == "drain_hp":
        dmg = random.randint(10, 22)
        player.hp -= dmg
        slow_print(clr(f"  A wraith passes through you! Life force drained! -{dmg} HP", MAGENTA))
    elif outcome == "drain_xp":
        lost = min(player.xp, random.randint(20, 40))
        player.xp -= lost
        slow_print(clr(f"  A dark vortex siphons your memories! -{lost} XP", MAGENTA))
    else:
        slow_print(clr("  The darkness recoils... you are spared this time.", CYAN))

def ev_drain_event(player, room_num):
    slow_print(clr("\n  🌊 Water rushes in through cracks in the walls!", CYAN))
    time.sleep(0.5)
    slow_print(clr("  You wade through the rising flood...", CYAN))
    dmg = random.randint(8, 20)
    player.hp -= dmg
    slow_print(clr(f"  The cold water saps your strength. -{dmg} HP", RED))
    if random.random() < 0.45:
        find = random.choice(["Health Potion", "Antidote", "Gold Coin"])
        slow_print(clr(f"  But you spot something floating by — {find}!", CYAN))
        player.inventory.append(find)
        if find == "Gold Coin":
            player.gold += 20
            player.inventory.remove(find)
            slow_print(clr("  +20g fished from the water.", YELLOW))

def ev_echo_challenge(player, room_num):
    slow_print(clr("\n  🔊 The Hall of Echoes demands a tribute of memory...", CYAN))
    time.sleep(0.5)
    length   = 4 + (room_num // 4)   
    sequence = [random.choice(["N", "S", "E", "W"]) for _ in range(length)]
    slow_print(clr(f"  Memorise this sequence ({length} steps): " + " ".join(sequence), YELLOW))
    time.sleep(0.8 + length * 0.4)
    os.system("cls" if os.name == "nt" else "clear")
    slow_print(clr("  Now enter the sequence (e.g.  N S E W):", BOLD))
    ans = input("  > ").strip().upper().split()
    if ans == sequence:
        reward = random.choice(["Greater Health Potion", "Rage Potion", "Chain Mail", "Elixir of Power"])
        slow_print(clr(f"  ✅ Perfect! The walls part and you claim: {reward}!", GREEN))
        player.inventory.append(reward)
    else:
        dmg = random.randint(12, 22)
        player.hp -= dmg
        slow_print(clr(f"  ❌ The echoes shriek and lash out! -{dmg} HP", RED))
        slow_print(clr(f"  (Sequence was: {' '.join(sequence)})", YELLOW))

def ev_look_around(player, room_num):
    """Flavour exploration beat — sometimes yields small bonuses."""
    finds = [
        ("  🕯  You find an old torch. It barely illuminates anything...", None),
        ("  💀  A skeleton slumped against the wall clutches a small pouch.", "gold_small"),
        ("  🗡  A dagger is lodged in the wall. Useless as a weapon but...", None),
        ("  📜  You find a torn note: 'Beware the third chest. It bites.'", None),
        ("  🧪  A cracked vial still holds a few drops of something red.", "heal_small"),
        ("  🕸  You disturb a massive cobweb. A spider scuttles off. Shudder.", None),
        ("  🪙  A few coins glint in a crack in the floor.", "gold_tiny"),
        ("  👁  You find scratches on the wall — someone counted days here.", None),
        ("  🌿  A patch of glowing moss. You press some against a wound.", "heal_tiny"),
        ("  🔑  You pocket a strange key. It fits nothing you've seen yet...", None),
        ("  📿  Beads on the floor — prayer beads from a long-dead adventurer.", None),
        ("  🩸  Blood trails lead to a corner. You wisely avoid it.", None),
        ("  ⚗  A bubbling cauldron sits cold and empty. Smells terrible.", None),
        ("  💎  A gem catches the light! You pocket it quickly.", "gold_medium"),
    ]
    msg, reward = random.choice(finds)
    slow_print(clr(f"\n{msg}", CYAN))
    if reward == "gold_small":
        g = random.randint(8, 18)
        player.gold += g
        slow_print(clr(f"  You loot the pouch. +{g}g!", YELLOW))
    elif reward == "gold_tiny":
        g = random.randint(3, 8)
        player.gold += g
        slow_print(clr(f"  +{g}g.", YELLOW))
    elif reward == "gold_medium":
        g = random.randint(20, 40)
        player.gold += g
        slow_print(clr(f"  You pocket the gem. +{g}g worth!", YELLOW))
    elif reward == "heal_small":
        healed = min(12, player.max_hp - player.hp)
        player.hp += healed
        slow_print(clr(f"  You drink it. +{healed} HP.", GREEN))
    elif reward == "heal_tiny":
        healed = min(6, player.max_hp - player.hp)
        player.hp += healed
        slow_print(clr(f"  Soothing... +{healed} HP.", GREEN))

def ev_empty(player, room_num):
    msgs = [
        "  🌫  Nothing here. The silence is deafening.",
        "  🕸  Just dust and cobwebs. You rest briefly.",
        "  👁  You feel watched. But there's nothing here.",
        "  💨  A cold draft chills you. Nothing stirs.",
        "  🌑  This corner of the dungeon feels truly forgotten.",
    ]
    slow_print(clr(f"\n{random.choice(msgs)}", CYAN))
    #NOTE: SMALL HEALING BONUS FOR RESTING IN AN EMPTY AREA
    if player.hp < player.max_hp:
        reg = random.randint(2, 5)
        player.hp = min(player.max_hp, player.hp + reg)
        slow_print(clr(f"  You catch your breath. +{reg} HP.", GREEN))

EVENT_DISPATCH = {
    "monster":       ev_monster,
    "ambush":        ev_ambush,
    "mimic":         ev_mimic,
    "item":          ev_item,
    "trap":          ev_trap,
    "puzzle":        ev_puzzle,
    "curse_room":    ev_curse_room,
    "drain_event":   ev_drain_event,
    "echo_challenge":ev_echo_challenge,
    "look_around":   ev_look_around,
    "empty":         ev_empty,
}

EVENT_LABELS = {
    "monster":        "⚔  Something moves ahead...",
    "ambush":         "💥 The room erupts into chaos!",
    "mimic":          "📦 Something glints in the corner...",
    "item":           "✨ You spot something on the ground...",
    "trap":           "⚠  The floor feels wrong underfoot...",
    "puzzle":         "🧩 An inscription glows on the wall...",
    "curse_room":     "💀 A dark presence lingers here...",
    "drain_event":    "🌊 Water begins seeping through the walls...",
    "echo_challenge": "🔊 The room hums with strange resonance...",
    "look_around":    "👁  You carefully scan the room...",
    "empty":          "🌫  The area seems quiet...",
}

#NOTE: FULL ROOM EXPLORATION LOOP
def explore_room(player, room, room_num):
    """
    Runs through all encounter slots in the room one by one.
    After each event the player can: continue, use inventory, check status, or try to leave early.
    """
    encounter_list = random.choice(room["encounters"])
    total = len(encounter_list)

    for idx, event in enumerate(encounter_list):
        if player.hp <= 0:
            break

        os.system("cls" if os.name == "nt" else "clear")
        player.status()

        progress = clr(f"[{idx+1}/{total}]", YELLOW)
        print(clr(f"\n  🚪 {room['name']}  {progress}", BOLD))
        hr()

        label = EVENT_LABELS.get(event, "...")
        slow_print(clr(f"\n  {label}", CYAN))
        time.sleep(0.35)

        handler = EVENT_DISPATCH.get(event, ev_empty)
        handler(player, room_num)

        if player.hp <= 0:
            break

        is_last = (idx == total - 1)
        print()
        hr()
        if is_last:
            slow_print(clr("  You reach the far door. Room complete!", GREEN))
        else:
            print(clr("  [1] Press on   [2] Use item   [3] Status   [4] Bail out (lose room progress)", BOLD))
            act = input("  > ").strip()
            if act == "2":
                inventory_menu(player)  # fix: replaced with unified inventory_menu
            elif act == "3":
                player.status()
                pause()
            elif act == "4":
                slow_print(clr("  You retreat back to the corridor. Progress lost.", YELLOW))
                return False   # room NOT cleared
            # "1" or anything else → continue

    return player.hp > 0   #NOTE: DON'T CHANGE THIS TO "RETURN TRUE" OR SOMETHING LIKE THAT BECAUSE THE FUNCTION CALLER RELIES ON THIS TO CHECK IF THE PLAYER DIED IN THE ROOM OR NOT

def shop(player):
    stock = {
        "Health Potion":         20,
        "Greater Health Potion": 45,
        "Antidote":              15,
        "Smoke Bomb":            30,
        "Iron Sword":            50,
        "Steel Sword":           110,
        "Leather Armor":         40,
        "Chain Mail":            90,
        "Elixir of Power":       70,
        "Rage Potion":           85,
    }
    while True:
        print(clr("\n  🏪 WANDERING MERCHANT", BOLD))
        print(f"     Gold: {clr(str(player.gold)+'g', YELLOW)}")
        hr()
        items = list(stock.items())
        for i, (itm, price) in enumerate(items, 1):
            col = GREEN if player.gold >= price else RED
            print(f"  {i}. {itm} — {clr(str(price)+'g', col)}  ({ITEMS[itm]['desc']})")
        print("  0. Leave")
        hr()
        c = input("  Buy which? > ").strip()
        if c == "0" or not c.isdigit(): break
        idx = int(c) - 1
        if 0 <= idx < len(items):
            itm, price = items[idx]
            if player.gold >= price:
                player.gold -= price
                player.inventory.append(itm)
                slow_print(clr(f"  ✅ Purchased {itm}!", GREEN))
                if ITEMS[itm]["type"] in ("weapon", "armor"):
                    if input(clr(f"  Equip {itm}? (y/n): ", BOLD)).strip().lower() == "y":
                        player.equip_item(itm)
            else:
                slow_print(clr("  ❌ Not enough gold!", RED))

def shrine(player):
    slow_print(clr("\n  ⛩  A glowing shrine pulses with warm light.", YELLOW))
    cost = 20
    if player.gold >= cost:
        if input(clr(f"  Offer {cost}g to heal 50% HP and cleanse curses? (y/n): ", BOLD)).strip().lower() == "y":
            player.gold -= cost
            healed = int(player.max_hp * 0.5)
            player.hp = min(player.max_hp, player.hp + healed)
            player.poisoned = False
            player.cursed   = False
            slow_print(clr(f"  ✨ +{healed} HP, all ailments cleansed!", GREEN))
    else:
        slow_print(clr(f"  You have no gold to offer ({cost}g needed).", YELLOW))

def run_game():
    os.system("cls" if os.name == "nt" else "clear")
    print(clr("""
╔════════════════════════════════════════╗
║         THE FORGOTTEN DUNGEON          ║
║      A Text-Based Adventure Game       ║
║             By: Adi Arjmnd             ║
╚════════════════════════════════════════╝
""", CYAN))

    slow_print("  You awaken in a dark dungeon. 12 rooms stand between you and freedom.")
    slow_print("  Each room hides multiple dangers. Stay sharp.\n")
    print(clr("  TIPS:", BOLD))
    print("  • Each room has 3-5 events — explore them all to clear the room")
    print("  • You can bail out mid-room but lose your progress")
    print("  • Shrines on rooms 4 & 8 heal you (costs gold)")
    print("  • Shop on rooms 3, 6 & 9 — save your gold!\n")

    name   = input(clr("  Enter your hero's name: ", BOLD)).strip() or "Hero"
    player = Player(name)
    slow_print(clr(f"\n  Brave yourself, {name}. The dungeon does not forgive.\n", YELLOW))
    time.sleep(1)

    total_rooms = 12
    used_rooms  = []   #NOTE: DO NOT USE THE SAME ROOM TWICE IN A ROW UNLESS THERE ARE LESS THAN 3 ROOMS LEFT TO CHOOSE FROM

    while player.hp > 0 and player.rooms_cleared < total_rooms:
        os.system("cls" if os.name == "nt" else "clear")
        player.status()
        room_num = player.rooms_cleared + 1
        print(clr(f"  🗺  Room {room_num} of {total_rooms}", BOLD))

        if player.poisoned or player.weapon == "Cursed Blade":
            slow_print(clr("\n  ⏳ Status effects tick...", YELLOW))
            died = player.tick_status()  # fix: use return value instead of re-checking hp
            if died: break

        #NOTE: THIS IS THE ONLY PLACE IN THE GAME WHERE ROOM 5 CAN BE SPECIAL NOW IT HAS A TINY CHANCE TO SPAWN A LEGENDARY SWORD THAT KILLS ANY MONSTER IN ONE HIT AND LOOKS REALLY COOL THE NAME OF THE SWORD IS A REFERENCE IS I'AM CUZ I LOVE ANGELS <3
        if room_num == 5:
            roll = random.random()
            if roll < 0.00001:
                hr2()
                slow_print(clr("  ✨✨✨ A blinding golden light fills the chamber! ✨✨✨", YELLOW))
                time.sleep(1)
                slow_print(clr("  A divine two-handed blade descends from above!", YELLOW))
                slow_print(clr("  ⚔  You have found: Angelic Addie's Sword!", YELLOW))
                slow_print(clr("  It can slay ANY creature in a single strike.", CYAN))
                player.inventory.append("Angelic Addie's Sword")
                if input(clr("  Equip it? (y/n): ", BOLD)).strip().lower() == "y":
                    player.equip_item("Angelic Addie's Sword")
                hr2()
            else:
                slow_print(clr(f"\n  🌟 Room 5: A divine presence flickers... and vanishes. (Roll: {roll:.6f})", CYAN))

        if room_num in (4, 8):
            shrine(player)

        if room_num in (3, 6, 9):
            if input(clr("\n  A merchant steps from the shadows. Shop? (y/n): ", BOLD)).strip().lower() == "y":
                shop(player)

        candidates = [r for r in ROOMS if r not in used_rooms[-3:]]
        room = random.choice(candidates if candidates else ROOMS)
        used_rooms.append(room)

        print(clr(f"\n  You push open the door...", CYAN))
        time.sleep(0.4)
        hr()
        slow_print(clr(f"  ▶  {room['name']}", BOLD))
        slow_print(clr(f"  {room['desc']}", CYAN))
        hr()
        pause("  [Press Enter to begin exploring...]")

        cleared = explore_room(player, room, room_num)

        if player.hp <= 0: break

        if cleared:
            player.rooms_cleared += 1
            os.system("cls" if os.name == "nt" else "clear")
            player.status()
            slow_print(clr(f"  ✅ Room {room_num} cleared! ({player.rooms_cleared}/{total_rooms})", GREEN))
        else:
            slow_print(clr("  You stumble back. The room remains unconquered.", YELLOW))

        if player.hp > 0:
            pause()

    #FIXED: ENDGAME SCREEN WASNT SHOWING IF YOU DIED IN THE LAST ROOM NOW IT DOES
    os.system("cls" if os.name == "nt" else "clear")
    hr2()
    if player.hp <= 0:
        slow_print(clr("""
  ☠  YOU HAVE FALLEN ☠

  The dungeon swallows you whole.
  Another soul lost to the darkness forever.
""", RED))
    else:
        slow_print(clr("""
  🏆  VICTORY! YOU ESCAPED! 🏆

  Against all odds you clawed your way out
  of the Forgotten Dungeon. A legend is born.
""", YELLOW))

    hr2()
    print(clr("  ─── Final Stats ───────────────────────────", CYAN))
    print(f"    Hero:    {player.name}")
    print(f"    Level:   {player.level}")
    print(f"    Gold:    {player.gold}g")
    print(f"    Kills:   {player.kills}")
    print(f"    Rooms:   {player.rooms_cleared}/{total_rooms}")
    hr2()

    # End of run_game()

# fix: replaced recursion with loop — prevents stack overflow on repeated replays
def main():
    while True:
        run_game()
        if input(clr("\n  Play again? (y/n): ", BOLD)).strip().lower() != "y":
            slow_print(clr("\n  Farewell, adventurer. May your next life be kinder.\n", CYAN))
            break

if __name__ == "__main__":
    main()
