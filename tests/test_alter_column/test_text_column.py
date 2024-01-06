from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import MetaData, Table, Column, TEXT, insert
from sqlalchemy.dialects import postgresql

if TYPE_CHECKING:
    from sqlalchemy import Connection

from tests.base.render_and_run import compare_and_run


class NewEnum(Enum):
    A = "a"
    B = "b"
    C = "c"


def test_text_column(connection: "Connection"):
    database_schema = MetaData()
    a_table = Table("a", database_schema, Column("value", TEXT))
    database_schema.create_all(connection)
    connection.execute(
        insert(a_table).values(
            [
                {"value": NewEnum.A.name},
                {"value": NewEnum.B.name},
                {"value": NewEnum.B.name},
                {"value": NewEnum.C.name},
            ]
        )
    )

    target_schema = MetaData()
    Table("a", target_schema, Column("value", postgresql.ENUM(NewEnum)))

    compare_and_run(
        connection,
        target_schema,
        expected_upgrade=f"""
        # ### commands auto generated by Alembic - please adjust! ###
        sa.Enum('A', 'B', 'C', name='newenum').create(op.get_bind())
        op.alter_column('a', 'value',
                   existing_type=sa.TEXT(),
                   type_=postgresql.ENUM('A', 'B', 'C', name='newenum'),
                   existing_nullable=True,
                   postgresql_using='value::newenum')
        # ### end Alembic commands ###
    """,
        expected_downgrade=f"""
        # ### commands auto generated by Alembic - please adjust! ###
        op.alter_column('a', 'value',
                   existing_type=postgresql.ENUM('A', 'B', 'C', name='newenum'),
                   type_=sa.TEXT(),
                   existing_nullable=True)
        sa.Enum('A', 'B', 'C', name='newenum').drop(op.get_bind())
        # ### end Alembic commands ###    
    """,
    )
