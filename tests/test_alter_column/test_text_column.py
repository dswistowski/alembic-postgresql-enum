from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import MetaData, Table, Column, TEXT, insert
from sqlalchemy.dialects import postgresql

from tests.base.run_migration_test_abc import CompareAndRunTestCase

if TYPE_CHECKING:
    from sqlalchemy import Connection


class NewEnum(Enum):
    A = "a"
    B = "b"
    C = "c"


class TestTextColumn(CompareAndRunTestCase):
    def get_database_schema(self) -> MetaData:
        database_schema = MetaData()
        self.a_table = Table("a", database_schema, Column("value", TEXT))
        return database_schema

    def get_target_schema(self) -> MetaData:
        target_schema = MetaData()
        Table("a", target_schema, Column("value", postgresql.ENUM(NewEnum)))
        return target_schema

    def insert_migration_data(self, connection: "Connection"):
        connection.execute(
            insert(self.a_table).values(
                [
                    {"value": NewEnum.A.name},
                    {"value": NewEnum.B.name},
                    {"value": NewEnum.B.name},
                    {"value": NewEnum.C.name},
                ]
            )
        )

    def get_expected_upgrade(self) -> str:
        return """
            # ### commands auto generated by Alembic - please adjust! ###
            sa.Enum('A', 'B', 'C', name='newenum').create(op.get_bind())
            op.alter_column('a', 'value',
                       existing_type=sa.TEXT(),
                       type_=postgresql.ENUM('A', 'B', 'C', name='newenum'),
                       existing_nullable=True,
                       postgresql_using='value::newenum')
            # ### end Alembic commands ###
        """

    def get_expected_downgrade(self) -> str:
        return """
            # ### commands auto generated by Alembic - please adjust! ###
            op.alter_column('a', 'value',
                       existing_type=postgresql.ENUM('A', 'B', 'C', name='newenum'),
                       type_=sa.TEXT(),
                       existing_nullable=True)
            sa.Enum('A', 'B', 'C', name='newenum').drop(op.get_bind())
            # ### end Alembic commands ###    
        """
