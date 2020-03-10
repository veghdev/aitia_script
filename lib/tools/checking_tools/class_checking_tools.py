def is_class_attributes_defined(class_object, *args):
    missing_args = []
    for arg in args:
        if arg.startswith('__'):
            tmp = '_' + class_object.__class__.__name__ + arg
            if getattr(class_object, tmp) is None:
                missing_args.append(arg[2:])
        elif arg.startswith('_'):
            if getattr(class_object, arg) is None:
                missing_args.append(arg[1:])
        else:
            if getattr(class_object, arg) is None:
                missing_args.append(arg)
    assert len(missing_args) == 0, 'argument: {} is undefined'.format(', '.join(missing_args))
