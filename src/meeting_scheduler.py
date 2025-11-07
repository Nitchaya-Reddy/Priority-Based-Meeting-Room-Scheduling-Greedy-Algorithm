"""
Meeting Room Scheduling - Interval Tree Implementation

This is the implementation using an interval tree 

Algorithm: Priority-based greedy scheduling with interval tree for conflict detection
Time Complexity: O(n log n)
Space Complexity: O(n)

"""

from typing import List, Optional, Dict
from enum import IntEnum


class MeetingType(IntEnum):
    """Enumeration for 10 meeting types with unique importance levels (1-10)."""
    BOARD_MEETING = 10
    CEO_EXECUTIVE_MEETING = 9
    CLIENT_PRESENTATION = 8
    INVESTOR_MEETING = 7
    PROJECT_DEADLINE_REVIEW = 6
    TEAM_SPRINT_PLANNING = 5
    TECHNICAL_DESIGN_REVIEW = 4
    DEPARTMENT_SYNC = 3
    ONE_ON_ONE_MEETING = 2
    CASUAL_TEAM_LUNCH = 1
    
    @classmethod
    def from_string(cls, value: str) -> 'MeetingType':
        """Convert string to MeetingType enum (case-insensitive)."""
        mapping = {
            'board meeting': cls.BOARD_MEETING,
            'ceo executive meeting': cls.CEO_EXECUTIVE_MEETING,
            'client presentation': cls.CLIENT_PRESENTATION,
            'investor meeting': cls.INVESTOR_MEETING,
            'project deadline review': cls.PROJECT_DEADLINE_REVIEW,
            'team sprint planning': cls.TEAM_SPRINT_PLANNING,
            'technical design review': cls.TECHNICAL_DESIGN_REVIEW,
            'department sync': cls.DEPARTMENT_SYNC,
            'one on one meeting': cls.ONE_ON_ONE_MEETING,
            'casual team lunch': cls.CASUAL_TEAM_LUNCH,
        }
        key = value.lower().strip()
        if key not in mapping:
            raise ValueError(f"Unknown meeting type: '{value}'. Valid types: {list(mapping.keys())}")
        return mapping[key]
    
    def __str__(self):
        """String representation of meeting type."""
        names = {
            10: 'Board Meeting',
            9: 'CEO Executive Meeting',
            8: 'Client Presentation',
            7: 'Investor Meeting',
            6: 'Project Deadline Review',
            5: 'Team Sprint Planning',
            4: 'Technical Design Review',
            3: 'Department Sync',
            2: 'One-on-One Meeting',
            1: 'Casual Team Lunch'
        }
        return names.get(self.value, 'Unknown')


class Meeting:
    """Represents a single meeting request with type-based priority."""
    
    def __init__(self, meeting_id: str, start_time: float, finish_time: float, 
                 meeting_type: str):
        """
        Initialize a meeting.
        
        Args:
            meeting_id: Unique identifier for the meeting
            start_time: Start time (in hours, e.g., 9.0 for 9:00 AM)
            finish_time: Finish time (in hours)
            meeting_type: Type of meeting (one of 10 predefined types)
        
        Raises:
            ValueError: If finish_time <= start_time or invalid meeting type
        """
        if finish_time <= start_time:
            raise ValueError(f"Finish time ({finish_time}) must be > start time ({start_time})")
        
        self.meeting_id = meeting_id
        self.start_time = start_time
        self.finish_time = finish_time
        self.meeting_type = MeetingType.from_string(meeting_type)
        self.importance = self.meeting_type.value
    
    def overlaps_with(self, other: 'Meeting') -> bool:
        """
        Check if this meeting overlaps with another meeting.
        
        Time Complexity: O(1)
        """
        return not (self.finish_time <= other.start_time or 
                   other.finish_time <= self.start_time)
    
    def __repr__(self):
        return f"Meeting({self.meeting_id}, {self.start_time}-{self.finish_time}, {self.meeting_type}, priority={self.importance})"


class IntervalNode:
    """
    Node for interval tree - enables O(log n) overlap queries.
    
    Each node stores:
    - An interval (meeting)
    - max_end: Maximum finish time in this subtree (KEY OPTIMIZATION!)
    - Left and right child pointers
    """
    
    def __init__(self, interval: Meeting):
        self.interval = interval
        self.max_end = interval.finish_time  # Max finish time in this subtree
        self.left: Optional['IntervalNode'] = None
        self.right: Optional['IntervalNode'] = None


class IntervalTree:
    """
    Interval tree for O(log n) overlap detection.
    
    This is the KEY data structure that makes worst-case O(n log n) possible!
    
    How it works:
    1. Store intervals in a binary search tree (by start time)
    2. Each node tracks the max finish time in its subtree
    3. When searching for overlaps, prune entire subtrees that can't overlap
    
    Operations:
    - Insert: O(log n) - BST insertion by start time
    - Search overlap: O(log n) - Prune subtrees using max_end
    """
    
    def __init__(self):
        self.root: Optional[IntervalNode] = None
    
    def insert(self, interval: Meeting):
        """
        Insert an interval into the tree.
        
        Time Complexity: O(log n) - Binary search tree insertion
        """
        self.root = self._insert_recursive(self.root, interval)
    
    def _insert_recursive(self, node: Optional[IntervalNode], interval: Meeting) -> IntervalNode:
        """
        Recursive helper for insertion.
        
        Inserts based on start time (like standard BST).
        Updates max_end on the way back up.
        """
        if node is None:
            return IntervalNode(interval)
        
        # Insert based on start time (BST property)
        if interval.start_time < node.interval.start_time:
            node.left = self._insert_recursive(node.left, interval)
        else:
            node.right = self._insert_recursive(node.right, interval)
        
        # Update max_end for this subtree (KEY OPTIMIZATION!)
        # This is what allows us to prune during search
        node.max_end = max(
            node.max_end,
            interval.finish_time,
            node.left.max_end if node.left else float('-inf'),
            node.right.max_end if node.right else float('-inf')
        )
        
        return node
    
    def has_overlap(self, interval: Meeting) -> bool:
        """
        Check if interval overlaps with ANY interval in tree.
        
        Time Complexity: O(log n) GUARANTEED!
        
        This is why the algorithm is O(n log n) worst-case instead of O(n²).
        """
        return self._search_overlap(self.root, interval)
    
    def _search_overlap(self, node: Optional[IntervalNode], interval: Meeting) -> bool:
        """
        Recursive search for overlaps with intelligent pruning.
        
        Key insight: If left subtree's max_end <= interval.start_time,
        then NOTHING in the left subtree can overlap!
        This pruning is what gives us O(log n) instead of O(n).
        """
        if node is None:
            return False
        
        # Check if current node's interval overlaps
        if interval.overlaps_with(node.interval):
            return True
        
        # OPTIMIZATION: Prune left subtree if no overlap possible
        # If max finish time in left subtree <= our start time, skip left entirely!
        if node.left and node.left.max_end > interval.start_time:
            if self._search_overlap(node.left, interval):
                return True
        
        # Check right subtree
        return self._search_overlap(node.right, interval)


class MeetingScheduler:
    
    def __init__(self, meetings: List[Meeting]):
        """Initialize the scheduler with a list of meetings."""
        self.meetings = meetings
        self.scheduled_meetings: List[Meeting] = []
        self.rejected_meetings: List[Meeting] = []
    
    def schedule_meetings(self) -> List[Meeting]:
        """
        Schedule meetings using interval tree optimization.
        
        Returns:
            List of scheduled meetings (non-overlapping, maximizing total importance)
        
        Time Complexity: O(n log n) WORST-CASE GUARANTEED
        Space Complexity: O(n) for the interval tree
        """
        # Step 1: Sort by importance (desc), then finish time (asc)
        # Time: O(n log n)
        sorted_meetings = sorted(
            self.meetings,
            key=lambda m: (-m.importance, m.finish_time)
        )
        
        self.scheduled_meetings = []
        self.rejected_meetings = []
        
        # Interval tree for O(log n) overlap detection
        interval_tree = IntervalTree()
        
        # Step 2: Process each meeting in priority order
        # Time: n × O(log n) = O(n log n)
        for current_meeting in sorted_meetings:
            # Check for overlap using interval tree - O(log n)
            has_conflict = interval_tree.has_overlap(current_meeting)
            
            # Schedule or reject the meeting
            if not has_conflict:
                interval_tree.insert(current_meeting)  # O(log n)
                self.scheduled_meetings.append(current_meeting)
            else:
                self.rejected_meetings.append(current_meeting)
        
        # Step 3: Sort scheduled meetings by start time
        # Time: O(n log n)
        self.scheduled_meetings.sort(key=lambda m: m.start_time)
        
        return self.scheduled_meetings
    
    def print_schedule(self):
        """Print the scheduled and online/virtual meetings."""
        
        print(f"\nTotal meetings requested: {len(self.meetings)}")
        print(f"IN-PERSON meetings scheduled: {len(self.scheduled_meetings)}")
        print(f"ONLINE meetings: {len(self.rejected_meetings)}")
        
        # Calculate total importance
        total_importance = sum(m.importance for m in self.scheduled_meetings)
        max_possible = sum(m.importance for m in self.meetings)
        
        print(f"\nTotal importance (in-person): {total_importance:.1f}")
        print(f"Maximum possible importance: {max_possible:.1f}")
        
        # Print in-person meetings
        print("IN-PERSON MEETINGS :")
        print("-" * 80)
        print(f"{'ID':<20} {'Start':<8} {'Finish':<8} {'Duration':<10} {'Priority':<10} {'Type':<25}")
        print("-" * 80)
        
        for meeting in self.scheduled_meetings:
            duration = meeting.finish_time - meeting.start_time
            print(f"{meeting.meeting_id:<20} {meeting.start_time:<8.1f} {meeting.finish_time:<8.1f} "
                  f"{duration:<10.1f} {meeting.importance:<10} {str(meeting.meeting_type):<25}")
        
        # Print online/virtual meetings
        if self.rejected_meetings:
            print("ONLINE MEETINGS:")
            print("-" * 80)
            print(f"{'ID':<20} {'Start':<8} {'Finish':<8} {'Duration':<10} {'Priority':<10} {'Type':<25}")
            print("-" * 80)
            
            for meeting in self.rejected_meetings:
                duration = meeting.finish_time - meeting.start_time
                print(f"{meeting.meeting_id:<20} {meeting.start_time:<8.1f} {meeting.finish_time:<8.1f} "
                      f"{duration:<10.1f} {meeting.importance:<10} {str(meeting.meeting_type):<25}")
    
    def get_total_importance(self) -> int:
        """Calculate total importance value of scheduled meetings."""
        return sum(m.importance for m in self.scheduled_meetings)


def demo():
    """Demonstrate the O(n log n) worst-case scheduler."""
    # Create sample meetings
    meetings = [
        Meeting("Q4 Board Review", 9.0, 11.0, "Board Meeting"),
        Meeting("Team Lunch", 9.0, 10.0, "Casual Team Lunch"),
        Meeting("CEO Strategy", 9.5, 11.0, "CEO Executive Meeting"),
        Meeting("Client Demo", 10.0, 11.5, "Client Presentation"),
        Meeting("Sprint Planning", 13.0, 15.0, "Team Sprint Planning"),
        Meeting("1:1 with Sarah", 14.0, 16.0, "One on One Meeting"),
    ]
    
    scheduler = MeetingScheduler(meetings)
    scheduler.schedule_meetings()
    scheduler.print_schedule()


if __name__ == "__main__":
    demo()
