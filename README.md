# alembic-postgresql-enum
[<img src="https://img.shields.io/pypi/pyversions/alembic-postgresql-enum">](https://pypi.org/project/alembic-postgresql-enum/)
[<img src="https://img.shields.io/pypi/v/alembic-postgresql-enum">](https://pypi.org/project/alembic-postgresql-enum/)
[<img src="https://img.shields.io/pypi/l/alembic-postgresql-enum">](https://pypi.org/project/alembic-postgresql-enum/)

Alembic autogenerate support for creation, alteration and deletion of enums

Alembic will now automatically:
- Create enums that currently are not in postgres schema
- Remove/add/alter enum values
- Reorder enum values
- Delete unused enums from schema

## Usage

Install library:
```
pip install alembic-postgresql-enum
```

Add the line:

```python 
# env.py
import alembic_postgresql_enum
...
```

To the top of your migrations/env.py file.

## Features

* [Creation of enums](#creation-of-enum)
* [Deletion of unreferenced enums](#deletion-of-unreferenced-enum)
* [Creation of new enum values](#creation-of-new-enum-values)
* [Deletion of enums values](#deletion-of-enums-values)
* [Renaming of enum values](#rename-enum-value)

### Creation of enum
```python
class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class ExampleTable(BaseModel):
    test_field = Column(Integer, primary_key=True, autoincrement=False)
    enum_field = Column(sqlalchemy.Enum(MyEnum))
```
This code will generate migration given below: 
```python
def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('one', 'two', 'three', name='myenum').create(op.get_bind())
    op.add_column('example_table', sa.Column('enum_field', sa.Enum('one', 'two', 'three', name='myenum'), nullable=False))
    op.add_column('example_table', sa.Column('third_field', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('example_table', 'third_field')
    op.drop_column('example_table', 'enum_field')
    sa.Enum('one', 'two', 'three', name='myenum').drop(op.get_bind())
    # ### end Alembic commands ###
```

### Deletion of unreferenced enum
If enum is defined in postgres schema, but its mentions removed from code - I will be automatically removed
```python
class ExampleTable(BaseModel):
    test_field = Column(Integer, primary_key=True, autoincrement=False)
    # enum_field is removed
```

```python
def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('example_table', 'enum_field')
    sa.Enum('one', 'two', 'four', name='myenum').drop(op.get_bind())
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('one', 'two', 'four', name='myenum').create(op.get_bind())
    op.add_column('example_table', sa.Column('enum_field', postgresql.ENUM('one', 'two', 'four', name='myenum'), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
```

### Creation of new enum values

If new enum value is defined sync_enum_values function call will be added to migration to account for it

```python
class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4 # New enum value
```

```python
def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values('public', 'myenum', ['one', 'two', 'three', 'four'], 
                        [('example_table', 'enum_field')],
                        enum_values_to_rename=())
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values('public', 'myenum', ['one', 'two', 'three'], 
                        [('example_table', 'enum_field')],
                        enum_values_to_rename=())
    # ### end Alembic commands ###
```

### Deletion of enums values

If enum value is removed it also will be detected

```python
class MyEnum(enum.Enum):
    one = 1
    two = 2
    # three = 3 removed
```

```python
def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values('public', 'myenum', ['one', 'two'], 
                        [('example_table', 'enum_field')],
                        enum_values_to_rename=())
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values('public', 'myenum', ['one', 'two', 'three'], 
                        [('example_table', 'enum_field')],
                        enum_values_to_rename=())
    # ### end Alembic commands ###
```

### Rename enum value
In this case you must manually edit migration

```python
class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3 # renamed from `tree`
```

This code will generate this migration:
```python
def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values('public', 'myenum', ['one', 'two', 'three'], 
                        [('example_table', 'enum_field')],
                        enum_values_to_rename=())
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values('public', 'myenum', ['one', 'two', 'tree'], 
                        [('example_table', 'enum_field')],
                        enum_values_to_rename=())
    # ### end Alembic commands ###
```

This migration will cause problems with existing rows that references MyEnum

So adjust migration like that

```python
def upgrade():
    op.sync_enum_values('public', 'myenum', ['one', 'two', 'three'], 
                        [('example_table', 'enum_field')],
                        enum_values_to_rename=[('tree', 'three')])


def downgrade():
    op.sync_enum_values('public', 'myenum', ['one', 'two', 'tree'], 
                        [('example_table', 'enum_field')],
                        enum_values_to_rename=[('three', 'tree')])
```

Do not forget to switch places old and new values for downgrade
