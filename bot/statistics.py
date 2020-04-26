from django.db.models import Count, Avg, F

def stats_text():
    from .models import BotUser, MxmTrack, UserSession

    msg = "*Stats* \n"

    # Number of users
    msg += "Number of users: " + str(BotUser.objects.all().count()) + "\n"

    # Top songs
    track_fav = MxmTrack.objects.annotate(
            num_favorite=Count('botuser')
        ).exclude(
            num_favorite__lte=0
        )

    fav_number = min(10, len(track_fav))
    top_songs = track_fav.order_by('num_favorite')[:fav_number]
    msg += "Top " + str(fav_number) + " favorite songs:\n"

    for song in top_songs:
        msg += "- " + str(song) + "\n"

    # Average session length
    # avg_s = UserSession.objects.aggregate(
    #     average_session=Avg(F('end_time') - F('start_time'))
    # )
    # msg += "Average user session length: " + str(avg_s['average_session']) + "\n"

    return msg
