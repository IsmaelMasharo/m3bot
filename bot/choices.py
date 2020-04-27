
class MessageEventTypes:
    LYRICS = 'LY'
    FAVORITE = 'FA'
    COMMAND = 'CO'
    CHOICES = (
        (LYRICS, 'Lyrics'),
        (COMMAND, 'Command'),
        (FAVORITE, 'Favorite')
    )

class CommandTypes:
    STATISTICS = '/stats'
    FAVORITES = '/fav'

    LIST = [STATISTICS, FAVORITES]