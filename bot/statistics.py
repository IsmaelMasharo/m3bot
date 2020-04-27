from django.db.models import Count, Avg, F

def stats_text():
    from .models import BotUser, MxmTrack, UserSession

    msg = "*Estadisticas*\n"

    # Number of users
    msg += "Número de usuarios: %s\n" % str(BotUser.objects.all().count())

    # Top songs
    track_fav = MxmTrack.objects.annotate(
            num_favorite=Count('botuser')
        ).exclude(
            num_favorite__lte=0
        )

    fav_number = min(10, len(track_fav))
    top_songs = track_fav.order_by('num_favorite')[:fav_number]
    msg += "Top %s canciones favoritas:\n" % str(fav_number)

    for song in top_songs:
        msg += "- %s \n" % str(song)

    # Average user session
    avg_s = UserSession.objects.aggregate(
        average_session=Avg(F('end_time') - F('start_time'))
    )
    average = str(avg_s['average_session']).split(".")[0]
    msg += "Tiempo promedio por sesión: %s \n" % average

    return msg
