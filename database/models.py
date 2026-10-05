from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

# Fonte única da verdade do schema: o Alembic gera as migrations a partir daqui
# (ver migrations/env.py). Para mudar uma coluna, mude o model e rode
#   alembic revision --autogenerate -m "..."
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "Usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)


class Paciente(Base):
    __tablename__ = "Pacientes"
    __table_args__ = (Index("idx_pacientes_usuario", "usuario_id"),)

    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    id = Column(Integer, primary_key=True)
    nome = Column(String(150))
    telefone = Column(String(30))
    cpf = Column(String(20))

    consultas = relationship("Consulta", back_populates="paciente")


class Consulta(Base):
    __tablename__ = "Consultas"
    __table_args__ = (Index("idx_consultas_usuario", "usuario_id", "data"),)

    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("Pacientes.id"))
    data = Column(DateTime)
    tratamento = Column(String(150))
    valor = Column(Numeric(10, 2, asdecimal=False))
    metodo_pagamento = Column(String(50))
    compareceu = Column(Integer, default=0, server_default="0")
    pago = Column(Boolean, default=False, server_default="false")
    duracao = Column(Integer, nullable=False, default=30, server_default="30")

    paciente = relationship("Paciente", back_populates="consultas")


class Orcamento(Base):
    __tablename__ = "Orcamentos"
    __table_args__ = (Index("idx_orcamentos_usuario", "usuario_id"),)

    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    id = Column(Integer, primary_key=True)
    consulta_id = Column(Integer, ForeignKey("Consultas.id"))
    paciente_id = Column(Integer, ForeignKey("Pacientes.id"))
    valor = Column(Numeric(10, 2, asdecimal=False))
    forma_pagamento = Column(String(50))
    status = Column(Integer, default=0, server_default="0")
    data_criacao = Column(DateTime)


class Tratamento(Base):
    __tablename__ = "Tratamentos"
    __table_args__ = (Index("idx_tratamentos_usuario", "usuario_id"),)

    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    id = Column(Integer, primary_key=True)
    nome = Column(String(150))
    valor = Column(Numeric(10, 2, asdecimal=False))
    duracao = Column(Integer, nullable=True)
