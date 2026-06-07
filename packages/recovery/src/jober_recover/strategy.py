from __future__ import annotations

from dataclasses import dataclass

from jober_recover.taxonomy import FailureClass


@dataclass(frozen=True)
class RecoveryStrategy:
    name: str
    locator_mode: str
    description: str
    rediscover_form: bool = False
    clear_cookies: bool = False
    remember_mapping: bool = False


def propose_recovery_strategy(
    failure_class: FailureClass,
    *,
    attempt_index: int,
    platform: str | None = None,
) -> RecoveryStrategy:
    del platform
    if attempt_index <= 1:
        return RecoveryStrategy(
            name="primary_css",
            locator_mode="css",
            description="Use stable attribute selectors from discovery",
        )

    strategies: dict[FailureClass, list[RecoveryStrategy]] = {
        FailureClass.SELECTOR: [
            RecoveryStrategy(
                name="primary_css",
                locator_mode="css",
                description="Stable attribute selectors",
            ),
            RecoveryStrategy(
                name="label_role_fallback",
                locator_mode="label",
                description="Regenerate locator by accessible label/role",
                remember_mapping=True,
            ),
            RecoveryStrategy(
                name="text_near_field",
                locator_mode="text",
                description="Resolve by nearby label text",
                remember_mapping=True,
            ),
        ],
        FailureClass.NAVIGATION: [
            RecoveryStrategy(
                name="direct_url",
                locator_mode="css",
                description="Retry direct apply URL",
            ),
            RecoveryStrategy(
                name="reload_clear_cookies",
                locator_mode="css",
                description="Reload and clear site cookies",
                clear_cookies=True,
            ),
            RecoveryStrategy(
                name="careers_url_fallback",
                locator_mode="css",
                description="Fall back to careers page URL",
            ),
        ],
        FailureClass.FORM_DISCOVERY: [
            RecoveryStrategy(
                name="dom_scan",
                locator_mode="css",
                description="Standard DOM scan",
            ),
            RecoveryStrategy(
                name="a11y_tree_scan",
                locator_mode="label",
                description="Re-run discovery with accessibility tree emphasis",
                rediscover_form=True,
            ),
        ],
        FailureClass.UPLOAD: [
            RecoveryStrategy(
                name="file_chooser",
                locator_mode="css",
                description="Retry file chooser click",
            ),
            RecoveryStrategy(
                name="set_input_files_direct",
                locator_mode="label",
                description="Direct set_input_files on file input",
            ),
        ],
        FailureClass.VALIDATION: [
            RecoveryStrategy(
                name="standard_fill",
                locator_mode="label",
                description="Fill mapped values",
            ),
            RecoveryStrategy(
                name="validation_repair",
                locator_mode="label",
                description="Read validation errors and refill missing fields",
                rediscover_form=True,
            ),
        ],
    }

    chain = strategies.get(failure_class, [])
    if not chain:
        return RecoveryStrategy(
            name="generic_retry",
            locator_mode="label",
            description="Generic label-first retry",
        )
    idx = min(attempt_index - 1, len(chain) - 1)
    return chain[idx]
