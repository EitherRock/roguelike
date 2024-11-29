from typing import Callable, Optional


class TimedEntity:
    """Represents a timed entity in a circular linked list"""
    def __init__(
            self,
            current: int, target: object, rate: Callable[[object], int], cost: Callable[[object], int]
    ):
        self.current = current  # Current time track state
        self.target = target    # Target for callback
        self.rate = rate        # Rate callback function
        self.cost = cost        # Cost callback function
        self.prev: Optional['TimedEntity'] = None  # Previous record in the list
        self.next: Optional['TimedEntity'] = None  # Next record in the list


class TimeManager:
    """Manages the timed entities using a circular linked list."""
    def __init__(self):
        self.sentinel = TimedEntity(0, None, self.default_rate, self.default_cost)
        self.sentinel.prev = self.sentinel
        self.sentinel.next = self.sentinel
        self.release_time: Optional[TimedEntity] = None

    def default_rate(self, target: object) -> int:
        # A simple function to be used as the rate function
        return 0

    def default_cost(self, target: object) -> int:
        # A simple function to be used as the cost function
        return 0

    def register_timed_entity(
            self,
            current: int,
            target: object,
            rate: Callable[[object], int], cost: Callable[[object], int]
    ):
        """Adds a new timed entity to the circular linked list"""
        entity = TimedEntity(current=-current, target=target, rate=rate, cost=cost)
        entity.next = self.sentinel.next
        entity.prev = self.sentinel
        self.sentinel.next.prev = entity
        self.sentinel.next = entity

    def release_timed_entity(self):
        """Removes the next entity from the circular list and stores it for deallocation."""
        self.release_time = self.sentinel.next
        self.sentinel.next = self.release_time.next
        self.sentinel.next.prev = self.sentinel

    def progress_time_sentinel(self):
        """Moves the sentinel forward in the list and deallocates the released entity if necessary"""
        if self.release_time:
            self.release_time = None
        elif self.sentinel.next != self.sentinel and self.sentinel.next.next != self.sentinel:
            # Move sentinel one step forward
            x = self.sentinel.prev
            a = self.sentinel.next
            b = a.next
            a.prev = x
            x.next = a
            self.sentinel.prev = a
            self.sentinel.next = b
            a.next = self.sentinel
            b.prev = self.sentinel

    def progress_time(self):
        """Updates the current time value for the first entity in the list based on rate and cost functions."""
        if self.sentinel.next != self.sentinel:
            time = self.sentinel.next
            time.current += time.rate(time.target)
            while time.current >= 0:
                time.current -= time.cost(time.target)
                self.progress_time_sentinel()

    def display_entities(self):
        """Print the details of all registered entities."""
        current_entity = self.sentinel.next
        while current_entity != self.sentinel:  # Loop until we return to the sentinel
            print(f"Entity: {current_entity.target}, Current Time: {current_entity.current}")
            current_entity = current_entity.next


class GameTime:
    def __init__(self):
        self.sec = 0
        self.min = 0
        self.hour = 0
        self.day = 0
        self.year = 0

    def rate(self, _):
        """Rate at which time progresses."""
        return 1000  # Test with this one
        # return 100 <- use this one

    def update(self, _):
        """Update Game time variables"""
        print(f"Y:{self.year} D:{self.day} H:{self.hour} M:{self.min} S:{self.sec}")
        self.sec += 1
        if self.sec == 60:
            self.sec = 0
            self.min += 1
        if self.min == 60:
            self.min = 0
            self.hour += 1
        if self.hour == 24:
            self.hour = 0
            self.day += 1
        if self.day == 365:
            self.day = 0
            self.year += 1
        return 1000  # Cost of one action (one second)

    def __str__(self):
        return f"Y:{self.year} D:{self.day} {self.hour:02}:{self.min:02}"

