from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()

class BaseModel(object):
    RESOURCE_NAME = None
    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key,value in json_data.items():
            setattr(self, key, value)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        method = getattr(api_client, "get_{}".format(cls.RESOURCE_NAME))
        json_data = method(resource_id)
        return cls(json_data) #Example: People(json_data), which returns the class with initialized data: json_data
        

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        return eval("{}QuerySet()".format(cls.RESOURCE_NAME.title()))


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):
    RESOURCE_NAME = None
    
    def __init__(self):
        self.collection = []
        self.current_index = 0
        self.current_page = 1

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        mode = "get_{}".format(self.RESOURCE_NAME) #set the mode for either get_people or get_films.
        Model = eval(self.RESOURCE_NAME.title()) #set the Model for either People or Films.
        
        try:
            if self.current_index + 1 > len(self.collection): #check if we need to go to next page and fill collection.
                page_request = getattr(api_client, mode)(page = self.current_page) #Get the values for the next page.
    
                for element in page_request['results']: #Add each element in 'results' to the collection.
                    self.collection.append(Model(element))
                self.current_page += 1
                
            current_index = self.current_index
            self.current_index += 1    
            
            return self.collection[current_index]
            
        except SWAPIClientError:
            raise StopIteration

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        mode = "get_{}".format(self.RESOURCE_NAME)
        page_request = getattr(api_client, mode)
        return page_request()['count']

class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
