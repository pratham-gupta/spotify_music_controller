from rest_framework import serializers


search_type_choices = {"track":"track",
                        "artist":"artist",
                        "album":"album"
                        }

class SearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=50)
    query_type = serializers.MultipleChoiceField(choices=search_type_choices)

    # class Meta:
    #     fields = ('query', 'query_type')

class AddSongSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    song_uri = serializers.CharField(max_length=100)