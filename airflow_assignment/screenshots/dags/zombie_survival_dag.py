"""
Zombie Apocalypse Survival DAG

This DAG models the twice daily survival routine a small group of
survivors would actually run: once at dawn before anyone leaves the
bunker, and once at dusk before everyone locks down for the night.

Story flow

1. check_perimeter        looks for threats near the base and reports a
                           threat score plus a zombies_detected flag
2. scavenge_supplies       sends someone out for food and water and
                           reports back how many supply units were found
3. decide_response         looks at the threat score and branches the
                           run toward either engage_threat or
                           hide_and_wait. Whichever branch is not chosen
                           is skipped on purpose, and the logs explain
                           why.
4. engage_threat           only runs when a threat was actually found
5. hide_and_wait           only runs when the perimeter was clear
6. headcount_survivors     runs no matter which branch fired, and counts
                           how many survivors are present
7. radio_checkin           final task, radios the other camps with a
                           summary built from the data collected earlier
                           in the run

Data handed off with XCom

check_perimeter pushes threat_score and zombies_detected so the branch
task can make its call without repeating the perimeter check.
scavenge_supplies pushes supply_units so radio_checkin can report on
stock levels without querying anything again.
engage_threat and hide_and_wait each push a short outcome message so
radio_checkin can say what actually happened during the run.

Why this schedule

The routine has to run at shift change, not once a day. Dawn patrol at
06:00 clears the base before anyone goes out scavenging, and dusk
lockdown at 18:00 secures the base before nightfall. That is expressed
below with a two run per day cron schedule instead of a plain @daily.
"""

import random
from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.trigger_rule import TriggerRule


# Constants and environment specific values live here instead of being
# hardcoded inside task bodies. Anything that could reasonably change
# between environments is pulled from an Airflow Variable, with a
# sensible default so the DAG still runs on a fresh Airflow install.
THREAT_SCORE_ENGAGE_THRESHOLD = int(
    Variable.get("zombie_threat_engage_threshold", default_var=6)
)
MIN_SURVIVOR_HEADCOUNT = int(
    Variable.get("zombie_min_survivor_headcount", default_var=3)
)
BASE_CALLSIGN = Variable.get("zombie_base_callsign", default_var="BUNKER-7")

DEFAULT_ARGS = {
    "owner": "bunker_survivors",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def check_perimeter(**context):
    """Scan the perimeter and report a threat score.

    A real integration would call a sensor or a scout's radio report.
    Here the score is simulated so the DAG behaves differently from run
    to run, which is what lets the branch task actually branch.
    """
    log = context["ti"].log
    log.info("Starting perimeter scan around %s.", BASE_CALLSIGN)

    threat_score = random.randint(0, 10)
    zombies_detected = threat_score >= THREAT_SCORE_ENGAGE_THRESHOLD

    log.debug("Raw sensor reading before rounding: %s", threat_score)

    if zombies_detected:
        log.warning(
            "Threat score %s meets or exceeds the engage threshold of %s. "
            "Movement detected near the fence line.",
            threat_score,
            THREAT_SCORE_ENGAGE_THRESHOLD,
        )
    else:
        log.info(
            "Threat score %s is below the engage threshold of %s. "
            "Perimeter looks clear for now.",
            threat_score,
            THREAT_SCORE_ENGAGE_THRESHOLD,
        )

    context["ti"].xcom_push(key="threat_score", value=threat_score)
    context["ti"].xcom_push(key="zombies_detected", value=zombies_detected)
    log.info("Perimeter check complete. Results pushed to XCom.")


def decide_response(**context):
    """Choose the next branch based on the threat score from XCom.

    Returns the task_id of the single branch that should run. Airflow
    automatically marks the other branch as skipped, which is the
    deliberate skip this assignment asks for.
    """
    log = context["ti"].log
    ti = context["ti"]

    threat_score = ti.xcom_pull(task_ids="check_perimeter", key="threat_score")
    zombies_detected = ti.xcom_pull(
        task_ids="check_perimeter", key="zombies_detected"
    )

    log.info(
        "Read threat_score=%s and zombies_detected=%s from check_perimeter.",
        threat_score,
        zombies_detected,
    )

    if zombies_detected:
        log.critical(
            "Zombies detected with threat score %s. Routing to "
            "engage_threat. hide_and_wait will be skipped this run.",
            threat_score,
        )
        return "engage_threat"

    log.info(
        "No zombies detected, threat score %s stayed under threshold. "
        "Routing to hide_and_wait. engage_threat will be skipped this run.",
        threat_score,
    )
    return "hide_and_wait"


def engage_threat(**context):
    """Fight branch, only reached when the perimeter check found a threat."""
    log = context["ti"].log
    threat_score = context["ti"].xcom_pull(
        task_ids="check_perimeter", key="threat_score"
    )
    log.warning(
        "Engaging threat with score %s. All able bodied survivors called "
        "to the fence line.",
        threat_score,
    )
    outcome = f"Threat engaged and repelled, final threat score was {threat_score}."
    log.info(outcome)
    context["ti"].xcom_push(key="response_outcome", value=outcome)


def hide_and_wait(**context):
    """Flee and hide branch, reached when the perimeter check was clear."""
    log = context["ti"].log
    threat_score = context["ti"].xcom_pull(
        task_ids="check_perimeter", key="threat_score"
    )
    log.info(
        "Perimeter is clear at threat score %s. Sealing the doors and "
        "waiting this one out.",
        threat_score,
    )
    outcome = "No threat present, base stayed sealed and quiet."
    log.info(outcome)
    context["ti"].xcom_push(key="response_outcome", value=outcome)


def headcount_survivors(**context):
    """Count survivors present. Runs after either branch completes."""
    log = context["ti"].log
    survivor_count = random.randint(MIN_SURVIVOR_HEADCOUNT, MIN_SURVIVOR_HEADCOUNT + 5)

    log.info("Counting survivors currently inside %s.", BASE_CALLSIGN)

    if survivor_count < MIN_SURVIVOR_HEADCOUNT:
        log.error(
            "Survivor count %s is below the minimum expected headcount of %s. "
            "Someone may be missing.",
            survivor_count,
            MIN_SURVIVOR_HEADCOUNT,
        )
    else:
        log.info(
            "Survivor count %s meets the minimum expected headcount of %s.",
            survivor_count,
            MIN_SURVIVOR_HEADCOUNT,
        )

    context["ti"].xcom_push(key="survivor_count", value=survivor_count)
    log.debug("Headcount task finished pushing survivor_count to XCom.")


with DAG(
    dag_id="zombie_survival_dag",
    description="Twice daily survival routine for the bunker survivors.",
    default_args=DEFAULT_ARGS,
    schedule_interval="0 6,18 * * *",  # dawn patrol at 06:00, dusk lockdown at 18:00
    start_date=datetime(2026, 8, 1),
    catchup=False,
    max_active_runs=1,
    tags=["survival", "zombie", "capstone"],
) as dag:

    perimeter_task = PythonOperator(
        task_id="check_perimeter",
        python_callable=check_perimeter,
    )

    scavenge_task = BashOperator(
        task_id="scavenge_supplies",
        bash_command=(
            "echo 'Sending a scavenging party out for supplies.' && "
            "supply_units=$(( (RANDOM % 20) + 1 )) && "
            "echo \"Scavenging party returned with $supply_units supply units.\" && "
            "echo $supply_units"
        ),
        do_xcom_push=True,
    )

    branch_task = BranchPythonOperator(
        task_id="decide_response",
        python_callable=decide_response,
    )

    engage_task = PythonOperator(
        task_id="engage_threat",
        python_callable=engage_threat,
    )

    hide_task = PythonOperator(
        task_id="hide_and_wait",
        python_callable=hide_and_wait,
    )

    headcount_task = PythonOperator(
        task_id="headcount_survivors",
        python_callable=headcount_survivors,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    radio_checkin_task = BashOperator(
        task_id="radio_checkin",
        bash_command=(
            "echo 'Radioing other camps with the shift summary.' && "
            "echo \"Supply units on hand: {{ ti.xcom_pull(task_ids='scavenge_supplies') }}\" && "
            "echo \"Survivor headcount: "
            "{{ ti.xcom_pull(task_ids='headcount_survivors', key='survivor_count') }}\" && "
            "echo \"Response outcome: "
            "{{ ti.xcom_pull(task_ids=['engage_threat', 'hide_and_wait'], "
            "key='response_outcome') }}\" && "
            "echo 'Check in complete, going dark until next shift.'"
        ),
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    perimeter_task >> [scavenge_task, branch_task]
    branch_task >> [engage_task, hide_task] >> headcount_task
    scavenge_task >> radio_checkin_task
    headcount_task >> radio_checkin_task
