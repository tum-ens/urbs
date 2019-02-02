import pandas as pd
import pyomo.core as pyomo


def get_entity(instance, name):
    """ Retrieve values (or duals) for an entity in a model instance.

    Args:
        instance: a Pyomo ConcreteModel instance
        name: name of a Set, Param, Var, Constraint or Objective

    Returns:
        a Pandas Series with domain as index and values (or 1's, for sets) of
        entity name. For constraints, it retrieves the dual values
    """
    # magic: short-circuit if problem contains a result cache
    if hasattr(instance, '_result') and name in instance._result:
        return instance._result[name].copy(deep=True)

    # retrieve entity, its type and its onset names
    try:
        entity = instance.__getattribute__(name)
        labels = _get_onset_names(entity)
    except AttributeError:
        return pd.Series(name=name)

    # extract values
    if isinstance(entity, pyomo.Set):
        if entity.dimen > 1:
            results = pd.DataFrame([v + (1,) for v in entity.value])
        else:
            # Pyomo sets don't have values, only elements
            results = pd.DataFrame([(v, 1) for v in entity.value])

        # for unconstrained sets, the column label is identical to their index
        # hence, make index equal to entity name and append underscore to name
        # (=the later column title) to preserve identical index names for both
        # unconstrained supersets
        if not labels:
            labels = [name]
            name = name + '_'

    elif isinstance(entity, pyomo.Param):
        if entity.dim() > 1:
            results = pd.DataFrame(
                [v[0] + (v[1],) for v in entity.iteritems()])
        elif entity.dim() == 1:
            results = pd.DataFrame(
                [(v[0], v[1]) for v in entity.iteritems()])
        else:
            results = pd.DataFrame(
                [(v[0], v[1].value) for v in entity.iteritems()])
            labels = ['None']

    elif isinstance(entity, pyomo.Expression):
        if entity.dim() > 1:
            results = pd.DataFrame(
                [v[0]+(v[1](),) for v in entity.iteritems()])
        elif entity.dim() == 1:
            results = pd.DataFrame(
                [(v[0], v[1]()) for v in entity.iteritems()])
        else:
            results = pd.DataFrame(
                [(v[0], v[1]()) for v in entity.iteritems()])
            labels = ['None']

    elif isinstance(entity, pyomo.Constraint):
        if entity.dim() > 1:
            # check whether all entries of the constraint have an existing dual variable
            # in that case add to results
            results = pd.DataFrame(
                [key + (instance.dual[entity.__getitem__(key)],)
                 for (id, key) in entity.id_index_map().items() if id in instance.dual._dict.keys()])
        elif entity.dim() == 1:
            results = pd.DataFrame(
                [(v[0], instance.dual[v[1]]) for v in entity.iteritems()])
        else:
            results = pd.DataFrame(
                [(v[0], instance.dual[v[1]]) for v in entity.iteritems()])
            labels = ['None']

    else:
        # create DataFrame
        if entity.dim() > 1:
            # concatenate index tuples with value if entity has
            # multidimensional indices v[0]
            results = pd.DataFrame(
                [v[0] + (v[1].value,) for v in entity.iteritems()])
        elif entity.dim() == 1:
            # otherwise, create tuple from scalar index v[0]
            results = pd.DataFrame(
                [(v[0], v[1].value) for v in entity.iteritems()])
        else:
            # assert(entity.dim() == 0)
            results = pd.DataFrame(
                [(v[0], v[1].value) for v in entity.iteritems()])
            labels = ['None']

    # check for duplicate onset names and append one to several "_" to make
    # them unique, e.g. ['sit', 'sit', 'com'] becomes ['sit', 'sit_', 'com']
    for k, label in enumerate(labels):
        if label in labels[:k] or label == name:
            labels[k] = labels[k] + "_"

    if not results.empty:
        # name columns according to labels + entity name
        results.columns = labels + [name]
        results.set_index(labels, inplace=True)

        # convert to Series
        results = results[name]
    else:
        # return empty Series
        results = pd.Series(name=name)
    return results


def get_entities(instance, names):
    """ Return one DataFrame with entities in columns and a common index.

    Works only on entities that share a common domain (set or set_tuple), which
    is used as index of the returned DataFrame.

    Args:
        instance: a Pyomo ConcreteModel instance
        names: list of entity names (as returned by list_entities)

    Returns:
        a Pandas DataFrame with entities as columns and domains as index
    """

    df = pd.DataFrame()
    for name in names:
        other = get_entity(instance, name)

        if df.empty:
            df = other.to_frame()
        else:
            index_names_before = df.index.names

            df = df.join(other, how='outer')

            if index_names_before != df.index.names:
                df.index.names = index_names_before

    return df


def list_entities(instance, entity_type):
    """ Return list of sets, params, variables, constraints or objectives

    Args:
        instance: a Pyomo ConcreteModel object
        entity_type: "set", "par", "var", "con" or "obj"

    Returns:
        DataFrame of entities

    Example:
        >>> data = read_excel('mimo-example.xlsx')
        >>> model = create_model(data, range(1,25))
        >>> list_entities(model, 'obj')  #doctest: +NORMALIZE_WHITESPACE
                                         Description Domain
        Name
        obj   minimize(cost = sum of all cost types)     []

    """

    # helper function to discern entities by type
    def filter_by_type(entity, entity_type):
        if entity_type == 'set':
            return isinstance(entity, pyomo.Set) and not entity.virtual
        elif entity_type == 'par':
            return isinstance(entity, pyomo.Param)
        elif entity_type == 'var':
            return isinstance(entity, pyomo.Var)
        elif entity_type == 'con':
            return isinstance(entity, pyomo.Constraint)
        elif entity_type == 'obj':
            return isinstance(entity, pyomo.Objective)
        else:
            raise ValueError("Unknown entity_type '{}'".format(entity_type))

    # create entity iterator, using a python 2 and 3 compatible idiom:
    # http://python3porting.com/differences.html#index-6
    try:
        iter_entities = instance.__dict__.iteritems()  # Python 2 compat
    except AttributeError:
        iter_entities = instance.__dict__.items()  # Python way

    # now iterate over all entties and keep only those whose type matches
    entities = sorted(
        (name, entity.doc, _get_onset_names(entity))
        for (name, entity) in iter_entities
        if filter_by_type(entity, entity_type))

    # if something was found, wrap tuples in DataFrame, otherwise return empty
    if entities:
        entities = pd.DataFrame(entities,
                                columns=['Name', 'Description', 'Domain'])
        entities.set_index('Name', inplace=True)
    else:
        entities = pd.DataFrame()
    return entities


def _get_onset_names(entity):
    """ Return a list of domain set names for a given model entity

    Args:
        entity: a member entity (i.e. a Set, Param, Var, Objective, Constraint)
                of a Pyomo ConcreteModel object

    Returns:
        list of domain set names for that entity

    Example:
        >>> data = read_excel('mimo-example.xlsx')
        >>> model = create_model(data, range(1,25))
        >>> _get_onset_names(model.e_co_stock)
        ['t', 'sit', 'com', 'com_type']
    """
    # get column titles for entities from domain set names
    labels = []

    if isinstance(entity, pyomo.Set):
        if entity.dimen > 1:
            # N-dimensional set tuples, possibly with nested set tuples within
            if entity.domain:
                # retreive list of domain sets, which itself could be nested
                domains = entity.domain.set_tuple
            else:
                try:
                    # if no domain attribute exists, some
                    domains = entity.set_tuple
                except AttributeError:
                    # if that fails, too, a constructed (union, difference,
                    # intersection, ...) set exists. In that case, the
                    # attribute _setA holds the domain for the base set
                    try:
                        domains = entity._setA.domain.set_tuple
                    except AttributeError:
                        # if that fails, too, a constructed (union, difference,
                        # intersection, ...) set exists. In that case, the
                        # attribute _setB holds the domain for the base set
                        domains = entity._setB.domain.set_tuple

            for domain_set in domains:
                labels.extend(_get_onset_names(domain_set))

        elif entity.dimen == 1:
            if entity.domain:
                # 1D subset; add domain name
                labels.append(entity.domain.name)
            else:
                # unrestricted set; add entity name
                labels.append(entity.name)
        else:
            # no domain, so no labels needed
            pass

    elif isinstance(entity, (pyomo.Param, pyomo.Var, pyomo.Expression,
                     pyomo.Constraint, pyomo.Objective)):
        if entity.dim() > 0 and entity._index:
            labels = _get_onset_names(entity._index)
        else:
            # zero dimensions, so no onset labels
            pass

    else:
        raise ValueError("Unknown entity type!")

    return labels
