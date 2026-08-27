"""Smoke sweep over every named non-admin route.

This is the automated form of "boot runserver and click around". It catches
template syntax errors, NoReverseMatch in templates, removed fields referenced
by a view or template, import errors, and most dependency-bump breakage.

Route args are resolved generically from ``view_class.model`` / ``.queryset``,
which covers the large majority with no per-route code. Anything that can't be
resolved gets an entry in URL_KWARGS below.
"""
import pytest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import NoReverseMatch, get_resolver, reverse
from django.urls.resolvers import URLPattern, URLResolver


def _walk(resolver, namespace='', inherited=frozenset()):
    """Yield (name, argnames, callback) for every named pattern.

    Args are accumulated from parent resolvers -- most `slug` kwargs come from a
    parent include() prefix, so reading the leaf pattern alone under-reports.
    """
    for pattern in resolver.url_patterns:
        groups = frozenset(pattern.pattern.regex.groupindex.keys())
        if isinstance(pattern, URLResolver):
            prefix = f'{pattern.namespace}:' if pattern.namespace else ''
            yield from _walk(pattern, namespace + prefix, inherited | groups)
        elif isinstance(pattern, URLPattern) and pattern.name:
            yield namespace + pattern.name, inherited | groups, pattern.callback


def _collect_routes():
    routes = [r for r in _walk(get_resolver()) if not r[0].startswith('admin:')]
    return sorted(routes, key=lambda r: r[0])


ROUTES = _collect_routes()

# Routes whose kwargs can't be derived from the view class. Values are either a
# literal dict, or a callable taking the seed_data dict.
URL_KWARGS = {
    'password_reset_confirm': {'uidb64': 'MQ', 'token': 'set-password'},
    # slug identifies the Student; pk is only used to build the success_url.
    'people:prospect compliance form': lambda seed: {
        'slug': seed['students'][0].slug, 'pk': seed['prospect'].pk,
    },
    # These views declare no model, so the pk has to be named explicitly.
    'people:signup success': lambda seed: {'pk': seed['test_event'].pk},
    'sections:drop enrollment': lambda seed: {'pk': seed['enrollments'][0].pk},
    'sections:cancel class task': lambda seed: {'pk': seed['cancellation'].pk},
    'assessments:send tabe score report': lambda seed: {
        'slug': seed['students'][0].slug, 'pk': seed['tabe'].pk,
    },
    'assessments:send clas-e score report': lambda seed: {
        'slug': seed['students'][0].slug, 'pk': seed['clas_e'].pk,
    },
    'assessments:test event csv': lambda seed: {'pk': seed['test_event'].pk},
    'assessments:tabe online csv': lambda seed: {'pk': seed['test_event'].pk},
    'assessments:test event attendance report': (
        lambda seed: {'pk': seed['test_event'].pk}
    ),
}

# Routes that are genuinely broken in the app, not in this harness. Marked
# xfail(strict=True) so the suite stays green while still telling us the moment
# one gets fixed -- at which point delete the entry.
KNOWN_BROKEN = {
    'assessments:student accuplacer detail': (
        'assessments/student_accuplacer_detail.html does not exist -- every '
        'sibling test type has one. Related: Accuplacer and Gain are the only '
        'test models without get_absolute_url, and StudentTestAddView is a '
        'CreateView with no success_url, so submitting the Add form for either '
        'raises ImproperlyConfigured'
    ),
}

# Routes excluded from the sweep, with the reason. Keep this list short and
# always justified -- it is where coverage quietly goes to die.
SKIP_ROUTES = {
    'sections:g suite attendance': (
        'view calls the Google Classroom API once per student inside the '
        'request cycle (sections/views.py GSuiteAttendanceView); there is no '
        'seam to patch without mocking the view itself'
    ),
}

# Routes where a non-2xx/3xx status is the correct behaviour.
EXPECTED_STATUS = {
    # Django 5 requires POST to log out; GET returning 405 is correct.
    'logout': (405,),
}

# Kwarg values that don't come from a model instance.
LITERALS = {
    'attendance_date': '2026-01-07',
    'uidb64': 'MQ',
    'token': 'set-password',
}


def _seed_slug_for(name, seed_data):
    """Best-effort slug from the route name.

    Returns (value, strong). ``strong`` means the route name names the object
    type outright, so this beats ``view_class.model`` -- several views declare a
    model (Section, Coaching) whose slug is *not* what the URL captures.
    """
    if 'staff' in name or 'coachee' in name or name.endswith('update coachings'):
        return seed_data['teacher'].slug, True
    if 'prospect' in name:
        prospect = seed_data.get('prospect')
        return (getattr(prospect, 'slug', None), True)

    namespace = name.split(':')[0] if ':' in name else ''
    if namespace == 'sections':
        return seed_data['sections'][0].slug, False
    if namespace in ('people', 'coaching', 'assessments'):
        return seed_data['students'][0].slug, False
    return None, False


def _model_for(callback):
    view_class = getattr(callback, 'view_class', None)
    if view_class is None:
        return None
    model = getattr(view_class, 'model', None)
    if model is not None:
        return model
    queryset = getattr(view_class, 'queryset', None)
    if queryset is not None:
        return queryset.model
    return None


def _requires_login(callback):
    view_class = getattr(callback, 'view_class', None)
    if view_class is not None:
        return LoginRequiredMixin in view_class.__mro__
    # login_required() wrapped function views carry the original on __wrapped__
    return hasattr(callback, '__wrapped__')


def _build_kwargs(name, argnames, callback, seed_data):
    """Return (kwargs, confident).

    ``confident`` is False when any value was guessed rather than read off the
    view's own model, in which case the caller tolerates a 404.
    """
    if name in URL_KWARGS:
        override = URL_KWARGS[name]
        built = override(seed_data) if callable(override) else dict(override)
        return built, True

    kwargs = {}
    confident = True
    model = _model_for(callback)
    instance = model.objects.first() if model is not None else None

    for arg in argnames:
        if arg in LITERALS:
            kwargs[arg] = LITERALS[arg]
            confident = False
        elif arg == 'student_slug':
            kwargs[arg] = seed_data['students'][0].slug
        elif arg == 'staff_slug':
            kwargs[arg] = seed_data['teacher'].slug
        elif arg == 'category':
            kwargs[arg] = seed_data['category'].pk
        elif arg == 'slug':
            guess, strong = _seed_slug_for(name, seed_data)
            if strong and guess is not None:
                value, confident = guess, False
            else:
                value = getattr(instance, 'slug', None) if instance else None
                if value is None:
                    value, confident = guess, False
            if value is None:
                pytest.skip('no seed object to supply a slug')
            kwargs[arg] = value
        elif arg == 'pk':
            value = getattr(instance, 'pk', None) if instance is not None else None
            if value is None:
                pytest.skip('no seed object to supply a pk')
            kwargs[arg] = value
        else:
            pytest.skip(f'no seed value for kwarg {arg!r}')

    return kwargs, confident


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name,argnames,callback',
    ROUTES,
    ids=[r[0] for r in ROUTES],
)
def test_url_responds(request, auth_client, seed_data, name, argnames, callback):
    """Every named route renders for an authenticated staff user."""
    if name in SKIP_ROUTES:
        pytest.skip(SKIP_ROUTES[name])
    if name in KNOWN_BROKEN:
        request.node.add_marker(
            pytest.mark.xfail(reason=KNOWN_BROKEN[name], strict=True)
        )

    kwargs, confident = _build_kwargs(name, argnames, callback, seed_data)
    try:
        url = reverse(name, kwargs=kwargs)
    except NoReverseMatch as exc:
        pytest.skip(f'could not reverse: {exc}')

    allowed = EXPECTED_STATUS.get(name, (200, 302))
    if not confident:
        # A guessed kwarg may legitimately not exist; 404 is not a regression.
        allowed = allowed + (404,)

    response = auth_client.get(url, follow=False)
    assert response.status_code in allowed, (
        f'{name} -> {url} returned {response.status_code}'
    )


AUTH_ROUTES = [r for r in ROUTES if _requires_login(r[2])]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name,argnames,callback',
    AUTH_ROUTES,
    ids=[r[0] for r in AUTH_ROUTES],
)
def test_login_required(client, seed_data, name, argnames, callback):
    """Views declaring LoginRequiredMixin actually redirect anonymous users."""
    if name in SKIP_ROUTES:
        pytest.skip(SKIP_ROUTES[name])

    kwargs, _ = _build_kwargs(name, argnames, callback, seed_data)
    try:
        url = reverse(name, kwargs=kwargs)
    except NoReverseMatch as exc:
        pytest.skip(f'could not reverse: {exc}')

    response = client.get(url, follow=False)
    assert response.status_code == 302, (
        f'{name} -> {url} did not redirect anonymous user '
        f'(got {response.status_code})'
    )
    assert '/accounts/login' in response['Location'], (
        f'{name} redirected to {response["Location"]}, not the login page'
    )
