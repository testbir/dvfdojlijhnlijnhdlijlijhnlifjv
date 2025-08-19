# /catalog_service/alembic/versions/86c2cc90a1d2_cascade_fks_unique.py

"""cascade fks + unique

Revision ID: 86c2cc90a1d2
Revises: 21316c1ef0f0
Create Date: 2025-08-19 03:12:28.213324

"""

from alembic import op

revision = '86c2cc90a1d2'
down_revision = '21316c1ef0f0'
branch_labels = None
depends_on = None

def upgrade():
    # course_modals.course_id -> CASCADE + уникальность 1:1
    op.drop_constraint("course_modals_course_id_fkey", "course_modals", type_="foreignkey")
    op.create_foreign_key(
        "course_modals_course_id_fkey",
        "course_modals", "courses_course",
        ["course_id"], ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint("uq_course_modal_course", "course_modals", ["course_id"])

    # course_modal_blocks.modal_id -> CASCADE
    op.drop_constraint("course_modal_blocks_modal_id_fkey", "course_modal_blocks", type_="foreignkey")
    op.create_foreign_key(
        "course_modal_blocks_modal_id_fkey",
        "course_modal_blocks", "course_modals",
        ["modal_id"], ["id"],
        ondelete="CASCADE",
    )

    # student_works_sections.course_id -> CASCADE
    op.drop_constraint("student_works_sections_course_id_fkey", "student_works_sections", type_="foreignkey")
    op.create_foreign_key(
        "student_works_sections_course_id_fkey",
        "student_works_sections", "courses_course",
        ["course_id"], ["id"],
        ondelete="CASCADE",
    )

    # student_works.section_id -> CASCADE
    op.drop_constraint("student_works_section_id_fkey", "student_works", type_="foreignkey")
    op.create_foreign_key(
        "student_works_section_id_fkey",
        "student_works", "student_works_sections",
        ["section_id"], ["id"],
        ondelete="CASCADE",
    )

    # homepage_promo_images.course_id -> CASCADE
    op.drop_constraint("homepage_promo_images_course_id_fkey", "homepage_promo_images", type_="foreignkey")
    op.create_foreign_key(
        "homepage_promo_images_course_id_fkey",
        "homepage_promo_images", "courses_course",
        ["course_id"], ["id"],
        ondelete="CASCADE",
    )

def downgrade():
    op.drop_constraint("homepage_promo_images_course_id_fkey", "homepage_promo_images", type_="foreignkey")
    op.create_foreign_key("homepage_promo_images_course_id_fkey", "homepage_promo_images", "courses_course", ["course_id"], ["id"])

    op.drop_constraint("student_works_section_id_fkey", "student_works", type_="foreignkey")
    op.create_foreign_key("student_works_section_id_fkey", "student_works", "student_works_sections", ["section_id"], ["id"])

    op.drop_constraint("student_works_sections_course_id_fkey", "student_works_sections", type_="foreignkey")
    op.create_foreign_key("student_works_sections_course_id_fkey", "student_works_sections", "courses_course", ["course_id"], ["id"])

    op.drop_constraint("course_modal_blocks_modal_id_fkey", "course_modal_blocks", type_="foreignkey")
    op.create_foreign_key("course_modal_blocks_modal_id_fkey", "course_modal_blocks", "course_modals", ["modal_id"], ["id"])

    op.drop_constraint("uq_course_modal_course", "course_modals", type_="unique")
    op.drop_constraint("course_modals_course_id_fkey", "course_modals", type_="foreignkey")
    op.create_foreign_key("course_modals_course_id_fkey", "course_modals", "courses_course", ["course_id"], ["id"])
