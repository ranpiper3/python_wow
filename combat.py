from time import sleep

from command_router import route_in_combat_non_ending_turn_commands
from commands import pac_looting, get_available_paladin_abilities
from command_handler import prompt_revive
from entities import Character, Monster
from information_printer import print_loot_table


def engage_combat(character: Character, monster: Monster, alive_monsters: dict, guid_name_set: set, monster_GUID: int):
    """
    This is where we handle the turn based combat of the game
    available_spells - set of string commands that enable our character to use the spells he has available.

    First we get both parties to enter combat. We start the loop and have the monster attack and
    immediately check if the character is not dead from the blow.
    If not, we take his command and if said command is one that does not end the turn (ie. wants to print some
    information about the fight) we enter an inner loop handling such commands and
    which continues to take commands until it gets one that does end the turn.
    We handle the command (which is most likely a spell or auto attack) and check if the monster is dead.
    :param character: the player
    :param monster: the monster that the player has attacked
    Parameters below are used solely to delete the monster from the dict & set once he's dead
    :param alive_monsters: Dictionary with the alive monsters in the subzone the player is in
    :param guid_name_set: Set which holds the name of each monster_GUID
    :param monster_GUID: The monster GUID
    """
    # Load all of the currently available spells for our character
    available_spells: set() = get_available_spells(character)
    will_end_turn = True  # Dictates if we are going to count the iteration of the loop as a turn

    character.enter_combat()
    monster.enter_combat()
    if monster.gossip:  # if the monster has gossip
        monster.say_gossip()
        sleep(2)

    while character.is_in_combat():
        # We start off the combat with the monster dealing the first blow
        if not will_end_turn:  # skip attack if the turn has not ended
            # skip turn based things
            will_end_turn = True
        else:
            monster.start_turn_update()
            character.start_turn_update()

            if monster.is_alive():
                monster.attack(character)
            else:  # monster has died, most probably from a DoT
                handle_monster_death(character, monster, alive_monsters, guid_name_set, monster_GUID)
                break

        if not character.is_alive():
            monster.leave_combat()
            print(f'{monster.name} has slain character {character.name}')

            prompt_revive(character)
            break

        command = input()
        # check if the command does not end the turn, if it doesn't the same command gets returned
        command = route_in_combat_non_ending_turn_commands(command, character, monster)

        if command == 'attack':
            character.attack(monster)
        elif command in available_spells:
            # try to execute the spell and return if it managed to or not
            successful_cast = character.spell_handler(command, monster)
            if not successful_cast:
                # skip the next attack, don't count this iteration as a turn and load a command again
                will_end_turn = False

        if will_end_turn:
            monster.end_turn_update()
            character.end_turn_update()

        if not monster.is_alive():
            handle_monster_death(character, monster, alive_monsters, guid_name_set, monster_GUID)
            break


def handle_monster_death(character: Character, monster: Monster, alive_monsters: dict, guid_name_set: set, monster_GUID: int):
    """
    This function is called when a monster has just died
    :param character: the player's character
    :param monster_GUID: the unique GUID of the monster
    :param monster: the monster that has died
    :param alive_monsters:Dictionary with the alive monsters in the subzone the player is in
    :param guid_name_set: Set which holds the name of each monster_GUID
    """
    print(f'{character.name} has slain {monster.name}!')

    character.award_monster_kill(monster=monster, monster_guid=monster_GUID)
    character.leave_combat()  # will exit the combat loop on next iter

    del alive_monsters[monster_GUID]  # removes the monster from the dictionary
    guid_name_set.remove((monster_GUID, monster.name))  # remove it from the set used for looking up

    handle_loot(character, monster)


def handle_loot(character: Character, monster: Monster):
    """ Display the loot dropped from the monster and listen for input if the player wants to take any"""
    print_loot_table(monster.loot)
    while True:
        command = input()

        if command == 'take all':
            # takes everything

            gold = monster.give_loot('gold')
            if gold:  # if it's successful
                character.award_gold(gold)
                print(f'{character.name} has looted {gold} gold.')

            monster_loot = list(monster.loot.keys())  # list of strings, the item's names
            for item_name in monster_loot:
                # loop through them and get every one
                item: 'Item' = monster.give_loot(item_name=item_name)

                if item:  # if the loot is successful
                    character.award_item(item=item)
                    print(f'{character.name} has looted {item_name}.')

        elif "take" in command:
            item_name = command[5:]

            if item_name == "gold":
                gold = monster.give_loot("gold")

                if gold:  # if it's successful
                    character.award_gold(gold)
                    print(f'{character.name} has looted {gold} gold.')
            else:  # if we want to take an item
                item = monster.give_loot(item_name=item_name)

                if item:  # if the loot is successful
                    character.award_item(item=item)
                    print(f'{character.name} has looted {item_name}.')
        elif command == "?":
            pac_looting()
        elif command == "exit":  # end the looting process
            print('-' * 40)
            break
        else:
            print("Invalid command.")

        if not monster.loot:  # if the loot is empty, exit the loot window
            print('-' * 40)
            break

        print_loot_table(monster.loot)  # print the updated table each time we take something


# returns a set with a list of allowed commands (you can't cast a spell you haven't learned yet)
def get_available_spells(character: Character) -> set():
    chr_class = character.get_class()
    available_spells = set()

    if chr_class == 'paladin':
        available_spells = get_available_paladin_abilities(character)  # this function is from commands.py

    return available_spells
