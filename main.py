from __future__ import annotations
from typing import Iterable
from operator import attrgetter

from openai_api import ai_judge
from quizlet_api import get_cards


class Flashcard:
    """ A single flashcard """
    __slots__ = 'term', 'defi'

    def __init__(self, term: str, defi: str):
        self.term = term
        self.defi = defi

    def __repr__(self) -> str:
        return (f'Term:       {self.term}\n'
                f'Definition: {self.defi}')


class FlashDeck:
    """ A set of flashcards """
    def __init__(self, cards: Iterable[Flashcard] | None = None):
        if cards is not None:
            self._cards = list(cards)
        else:
            self._cards = []
            
        self._curr_idx = 0

    def __repr__(self) -> str:
        return '\n'.join(self._cards)

    def add_card(self, new_term: str, new_def: str) -> None:
        new_card = Flashcard(new_term, new_def)
        self._cards.append(new_card)
        self._curr_idx += 1

    def add_cards(
        self,
        new_terms: Iterable[str],
        new_defs: Iterable[str]
    ) -> None:
        new_pairs = zip(new_terms, new_defs)
        for new_term, new_def in new_pairs:
            self.add_card(new_term, new_def)

    @classmethod
    def from_list(cls, card_list: list[tuple]) -> FlashDeck:
        return cls([
            Flashcard(term, defi)
            for term, defi in card_list
        ])

    def pop_card(self) -> str:
        self._curr_idx -= 1
        return self._cards.pop()

    def peek_card(self) -> str:
        return self._cards[self._curr_idx]

    def go_back(self) -> bool:
        if self._curr_idx > 0:
            self._curr_idx -= 1
            return True
        return False
        
    def go_forward(self) -> bool:
        if self._curr_idx < len(self._cards) - 1:
            self._curr_idx += 1
            return True
        return False


def main():
    quizlet_url = input(
        'Please enter the URL of the quizlet you want to review:\n'
    )
    print('\nLoading cards...')
    card_list = get_cards(quizlet_url)
    card_deck = FlashDeck.from_list(card_list)
    mode = input(
        'Would you like to try [r/R]igid mode or [a/A]dvanced mode?\n'
        ' - Rigid mode: Your answer must be exactly '
        'the same as the correct answer.\n'
        ' - Advanced mode: An AI judger will grade '
        'your answer to see if they are right.\n'
    ).lower()
    if mode == 'r':
        print('Your answers to each term may be case-insensitive.')
    elif mode != 'a':
        print(
            'You didn\'t enter an available mode; '
            'the mode defaults to advanced mode.'
        )
        mode = 'a'
    
    correct_n = total_n = 0
    missed_cards = set()
    game_continue = True
    print()
    
    while game_continue:
        total_n += 1
        curr_card = card_deck.peek_card()
        print('Term:', curr_card.term)
        
        user_defi = input('Your answer: ')
        if (
            mode == 'r' and user_defi.lower() == curr_card.defi.lower() or
            mode == 'a' and ai_judge(curr_card.term, user_defi)
        ):
            print('Nice, you got this!')
            correct_n += 1
        else:
            print('Sorry, the correct answer is as follows:')
            print(curr_card.defi)
            missed_cards.add(curr_card)

        print()
        while True:
            next_op = input(
                'Enter [f/F] to move forward, '
                '[b/B] to go back, or '
                '[e/E] to end the review: '
            ).lower()
            if next_op == 'f':
                if card_deck.go_forward():
                    break
                else:
                    print(
                        'You cannot go forward as you are at the last card.'
                    )
            elif next_op == 'b':
                if card_deck.go_back():
                    break
                else:
                    print(
                        'You cannot go back as you are at the first card.'
                    )
            elif next_op == 'e':
                game_continue = False
                rate = correct_n / total_n
                print(f'Your correct rate is {rate:.3%}')
                if missed_cards:
                    print('You need practice on these cards:')
                    missed_cards = sorted(
                        missed_cards,
                        # Sort by term lexicographically
                        key=attrgetter('term')
                    )
                    print('\n'.join(map(repr, missed_cards)))
                break
        print()


if __name__ == '__main__':
    main()
