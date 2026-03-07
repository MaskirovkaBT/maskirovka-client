from dataclasses import dataclass, field

from domains.unit import Unit


@dataclass
class SearchState:
    eras: list = field(default_factory=list)
    factions: list = field(default_factory=list)
    types: list = field(default_factory=list)
    roles: list = field(default_factory=list)
    units: list[Unit] = field(default_factory=list)
    
    page: int = 1
    pages: int = 0
    sort_by: str = 'title'
    sort_order: str = 'asc'
    filters: dict = field(default_factory=dict)
    current_block: str = 'eras'
    
    def reset_pagination(self) -> None:
        self.page = 1
    
    def next_page(self) -> bool:
        if self.page < self.pages:
            self.page += 1
            return True
        return False
    
    def prev_page(self) -> bool:
        if self.page > 1:
            self.page -= 1
            return True
        return False
