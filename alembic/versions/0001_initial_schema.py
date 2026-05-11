"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-11

"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'usuarios',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('negocio_nombre', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)

    op.create_table(
        'periodos',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('usuario_id', sa.String(), nullable=False),
        sa.Column('año', sa.Integer(), nullable=False),
        sa.Column('mes', sa.Integer(), nullable=False),
        sa.Column('estado', sa.String(), nullable=False),
        sa.Column('resultado_neto', sa.Float(), nullable=True),
        sa.Column('total_inversiones_snapshot', sa.Float(), nullable=True),
        sa.Column('total_costos_fijos_snapshot', sa.Float(), nullable=True),
        sa.Column('ganancia_real', sa.Float(), nullable=True),
        sa.Column('ahorro', sa.Float(), nullable=True),
        sa.Column('inversion_siguiente', sa.Float(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_cierre', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_periodos_usuario_id'), 'periodos', ['usuario_id'], unique=False)

    op.create_table(
        'inversiones',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('periodo_id', sa.String(), nullable=False),
        sa.Column('descripcion', sa.String(), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('origen', sa.String(), nullable=False),
        sa.Column('creado_en', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_inversiones_periodo_id'), 'inversiones', ['periodo_id'], unique=False)

    op.create_table(
        'costos_fijos',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('costos_fijos')
    op.drop_index(op.f('ix_inversiones_periodo_id'), table_name='inversiones')
    op.drop_table('inversiones')
    op.drop_index(op.f('ix_periodos_usuario_id'), table_name='periodos')
    op.drop_table('periodos')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_table('usuarios')
