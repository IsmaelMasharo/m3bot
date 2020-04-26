from django.db.models import Count, Avg, F, Func

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
    return msg
    avg_s = UserSession.objects.annotate(
        duration = Func(F('end_date'), F('start_date'), function='age')
    )

    print(avg_s)
    return msg
    msg += "Average user session length: " + str(avg_s['average_session']) + "\n"

    return msg
