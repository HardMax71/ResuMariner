# Fixing the unique node nightmare in pydantic-neomodel-dict

## How it all went down

So there I was, thinking I had everything working perfectly. The resume parser was humming along, 
Neo4j was storing data beautifully, and then BAM - "Expected node of class TechnologyNode" errors started popping up everywhere. What the hell?

Turns out, the `pydantic-neomodel-dict` library I was using (v0.2.0) had this nasty bug that wasn't detected earlier. 
It completely choked when trying to handle nodes with unique constraints. And of course, I had unique constraints all over the place - for skills, technologies, companies.
I mean, you don't want seventeen different "Python" nodes in your database, right?

The whole thing took me down a rabbit hole that ended with me upgrading to v0.3.0, rebuilding all my Docker containers, 
and finally getting everything to work. Here's what actually happened under the hood.

## The problem that drove me crazy

Picture this: you've got a resume that mentions Python five times - once in skills, three times in different jobs, maybe once more in a project. 
In a sane world, your graph database should create ONE Python node and connect it to all those different places. That's the whole point of having unique constraints.

But here's what was actually happening with v0.2.0:

```python
# This is what should work
resume_data = {
    'uid': 'test-resume-001',
    'skills': [
        {'name': 'Python'},
        {'name': 'Docker', 'years': 5},
        {'name': 'Python'}  # Same Python!
    ]
}
```

Instead of creating one Python node and reusing it, the library would blow up with that cryptic "Expected node of class" error. Every. Single. Time.

## Why it was broken (the technical rabbit hole)

After digging through the library's source code (because of course the error messages were useless), I found the problem. 
When v0.2.0 tried to find existing nodes with unique properties, it did this incredibly stupid thing:

```python
existing = ogm_class.nodes.filter(**filter_data)
if existing:
    instance = existing[0]  # This is NOT what you think it is!
```

That `existing[0]` doesn't give you a real Neo4j node instance. It gives you this weird QuerySet proxy object that looks like a node but isn't really a node. 
It's like getting a picture of a sandwich when you're trying to eat lunch.

These proxy objects are cursed. They fail `isinstance()` checks, they don't have proper `element_id` attributes, and when neomodel's relationship manager tries to connect them, 
it basically says "what the hell is this thing you're trying to connect?" Hence the error.

The library was also completely ignoring the fact that nodes might have unique constraints. It would happily try to create duplicate nodes, 
then act surprised when Neo4j said "uh, no, that violates the unique constraint you set up."

## How v0.3.0 finally fixed it

When I saw the v0.3.0 release notes mentioning "Unique node handling in relationships", I nearly cried with relief. The maintainers finally figured out what was broken.

The fix was actually elegant once you see it. Instead of that filter() nonsense, they switched to using `get_or_create()`:

```python
# The fix that saved my sanity
if unique_filter:
    nodes = ogm_class.get_or_create(unique_filter)
    instance = nodes[0] if nodes else ogm_class()

    # Update any additional properties
    for key, value in data.items():
        if key not in unique_filter and key in defined:
            setattr(instance, key, value)

    instance.save()
    return instance
```

The `get_or_create()` method is magic. It either finds the existing node (as a real instance, not a proxy!) or creates a new one. No duplicates, no weird proxy objects, no crashes.

I've also added proper validation before trying to connect nodes. The library now checks if a node actually has an `element_id` before attempting to create relationships. 
If it doesn't, it saves the node first. Simple, but it prevented so many errors.

## Testing to make sure it actually worked

I created the most obnoxious test case I could think of - a resume with Python mentioned everywhere:

```python
resume_data = {
    'uid': 'duplicate-test',
    'skills': [
        {'name': 'Python', 'level': 'Expert'},
        {'name': 'Python', 'level': 'Advanced'}  # Duplicate!
    ],
    'employment_history': [
        {
            'company': {'name': 'TechCorp'},
            'technologies': [
                {'name': 'Python', 'version': '3.11'},
                {'name': 'Python', 'version': '3.12'}  # Another one!
            ]
        },
        {
            'company': {'name': 'TechCorp'},  # Same company again!
            'technologies': [
                {'name': 'Python'},  # And another Python!
            ]
        }
    ]
}
```

With v0.2.0, this would crash and burn. With v0.3.0? Smooth as butter.

I checked the database afterward, and it was beautiful:

```cypher
// Only ONE Python node in the entire database
MATCH (t:TechnologyNode {name: 'Python'})
RETURN count(t)  // Returns: 1 (not 5!)

// But multiple relationships pointing to it
MATCH ()-[r:USES_TECHNOLOGY]->(t:TechnologyNode {name: 'Python'})
RETURN count(r)  // Returns: 3 or more
```

One node, multiple relationships. Exactly how a graph database should work.

## What I learned from this mess

First off, QuerySet proxies are evil. I don't care how convenient they might seem for lazy loading or whatever - when you need a real instance, you need a real instance. 
The `filter()` method returning proxies instead of actual objects caused a couple of painful moments.

Second, always use `get_or_create()` for nodes with unique constraints. It's literally designed for this exact use case. 
Don't try to be clever with `filter()` and manually checking existence - you'll just end up with proxy objects and sadness.

Third, test with realistic, messy data. The bug only showed up when I had duplicate references to the same unique nodes. 
If I'd only tested with clean, non-duplicate data, I never would have caught this in development.

## The version evolution story

Looking back at the release notes, it's kind of funny how I've tried to fix this:

**v0.2.0** thought it was being smart by "extending the `_get_or_create_ogm_instance()` method to look up existing nodes before creating new ones." 
I've even replaced the `id()` function with a custom `stable_hash()` method for "better object tracking."

But `filter()` was still being used, still getting proxies, still failing.

**v0.3.0** just said "screw it" and did what they should have done from the beginning:
- Use `get_or_create()` for nodes with unique constraints
- Properly handle existing nodes in relationships
- Ensure all nodes have element_id before connecting

Three simple changes that fixed everything.

## The bottom line

If you're using pydantic-neomodel-dict and working with unique nodes (and let's be honest, you probably are), 
make sure you're on v0.3.0 or later. The fix from v0.2.0 to v0.3.0 is one of those changes that seems small in the release notes 
but makes the difference between "completely broken" and "actually works in production." Sometimes that's all you need - not a complete rewrite, just fixing the one stupid thing that breaks everything else.

And honestly? After spending a whole day debugging this, I'm just happy it works now. 
Sometimes that's the best documentation you can write - "it was broken, now it's fixed, here's why, please upgrade."

---

<details>
<summary>P.S. Plot twist...</summary>

Oh, by the way - guess who's the author of `pydantic-neomodel-dict`?

Yeah... it's me. (sic!)

I literally spent an hour or two debugging my own library, cursing at my past self for writing such broken code, and then fixing my own bugs. 
The "maintainers" I mentioned earlier? Also me. That elegant fix I praised? I wrote that too, after realizing what an idiot I'd been in v0.2.0.

This whole document is basically me roasting myself for not using `get_or_create()` from the beginning. But hey, at least I fixed it, right?

</details>

