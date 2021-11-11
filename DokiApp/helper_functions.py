from django.shortcuts import render


def result_page(request, result):
    return render(request, 'result.html', context={'result': result})


def entity_adapter(query_set, serializer_class):
    result = dict({})
    for item in query_set:
        user_serializer = serializer_class(instance=item)
        data = user_serializer.data
        result[item.id] = data
    return result
