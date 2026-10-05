"use strict";

/*
 * Frontend assessment workflow.
 *
 * Responsibilities:
 * - Load questionnaire definitions.
 * - Render all 50 questions.
 * - Track answered-question progress.
 * - Validate completion on the client side.
 * - Submit responses to POST /api/assessment.
 * - Render score, findings, and recommendations.
 *
 * The frontend never asks for or sends direct personal identifiers.
 */

const ASSESSMENT_API_BASE_URL =
    "http://127.0.0.1:5000";

let questionnaire = [];
let latestAssessment = null;


function assessmentElement(id) {
    return document.getElementById(id);
}


function setAssessmentError(
    message
) {
    const element = assessmentElement(
        "assessment-error"
    );

    if (!element) {
        return;
    }

    if (!message) {
        element.hidden = true;
        element.textContent = "";
        return;
    }

    element.hidden = false;
    element.textContent = message;

    element.scrollIntoView({
        behavior: "smooth",
        block: "center",
    });
}


function humanizeCategory(
    category
) {
    return String(category)
        .replaceAll("_", " ")
        .replace(/\b\w/g, (letter) =>
            letter.toUpperCase()
        );
}


function formatScore(
    value
) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return number.toFixed(1);
}


function riskLevelClass(
    riskLevel
) {
    return `result-risk-${String(
        riskLevel
    ).toLowerCase()}`;
}


function escapeText(
    value
) {
    return String(value ?? "");
}


async function assessmentFetchJson(
    endpoint,
    options = {}
) {
    const response = await fetch(
        `${ASSESSMENT_API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers: {
                "Accept": "application/json",
                ...(options.body
                    ? {
                        "Content-Type":
                            "application/json",
                    }
                    : {}),
                ...(options.headers || {}),
            },
        }
    );

    let data = null;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            `API returned a non-JSON response (HTTP ${response.status}).`
        );
    }

    if (!response.ok) {
        const message =
            data?.error?.message ||
            `Request failed with HTTP ${response.status}.`;

        throw new Error(message);
    }

    return data;
}


async function loadQuestionnaire() {
    const data =
        await assessmentFetchJson(
            "/api/questionnaire"
        );

    if (
        data.success !== true ||
        !Array.isArray(data.questions)
    ) {
        throw new Error(
            "Questionnaire API returned an unexpected response."
        );
    }

    if (data.questions.length !== 50) {
        throw new Error(
            `Expected 50 questions but received ${data.questions.length}.`
        );
    }

    questionnaire = data.questions;

    return data;
}


function groupQuestionsByCategory(
    questions
) {
    const groups = new Map();

    questions.forEach(
        (question) => {
            if (
                !groups.has(
                    question.category
                )
            ) {
                groups.set(
                    question.category,
                    []
                );
            }

            groups
                .get(question.category)
                .push(question);
        }
    );

    return groups;
}


function renderCategoryNavigation(
    groups
) {
    const container =
        assessmentElement(
            "category-navigation"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    groups.forEach(
        (questions, category) => {
            const button =
                document.createElement(
                    "button"
                );

            button.type = "button";
            button.className =
                "category-nav-button";

            button.dataset.category =
                category;

            const title =
                document.createElement(
                    "span"
                );

            title.textContent =
                humanizeCategory(
                    category
                );

            const count =
                document.createElement(
                    "span"
                );

            count.className =
                "category-count";

            count.textContent =
                `${questions.length} questions`;

            button.appendChild(title);
            button.appendChild(count);

            button.addEventListener(
                "click",
                () => {
                    const target =
                        document.getElementById(
                            `category-${category}`
                        );

                    if (target) {
                        target.scrollIntoView({
                            behavior: "smooth",
                            block: "start",
                        });
                    }
                }
            );

            container.appendChild(
                button
            );
        }
    );

    updateActiveCategory();
}


function renderQuestionnaire(
    questions
) {
    const container =
        assessmentElement(
            "questionnaire-container"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    const groups =
        groupQuestionsByCategory(
            questions
        );

    let categoryNumber = 0;

    groups.forEach(
        (categoryQuestions, category) => {
            categoryNumber += 1;

            const categorySection =
                document.createElement(
                    "section"
                );

            categorySection.className =
                "question-category";

            categorySection.id =
                `category-${category}`;

            const header =
                document.createElement(
                    "div"
                );

            header.className =
                "question-category-header";

            const eyebrow =
                document.createElement(
                    "p"
                );

            eyebrow.textContent =
                `Category ${categoryNumber}`;

            const title =
                document.createElement(
                    "h3"
                );

            title.textContent =
                humanizeCategory(
                    category
                );

            const count =
                document.createElement(
                    "span"
                );

            count.textContent =
                `${categoryQuestions.length} questions`;

            header.appendChild(eyebrow);
            header.appendChild(title);
            header.appendChild(count);

            categorySection.appendChild(
                header
            );

            categoryQuestions.forEach(
                (question) => {
                    categorySection.appendChild(
                        renderQuestion(
                            question
                        )
                    );
                }
            );

            container.appendChild(
                categorySection
            );
        }
    );

    attachAnswerListeners();
}


function renderQuestion(
    question
) {
    const wrapper =
        document.createElement(
            "article"
        );

    wrapper.className =
        "question-item";

    wrapper.dataset.questionId =
        question.id;

    const number =
        document.createElement(
            "span"
        );

    number.className =
        "question-number";

    number.textContent =
        question.id.replace(
            "Q",
            ""
        );

    const questionText =
        document.createElement(
            "p"
        );

    questionText.className =
        "question-text";

    questionText.textContent =
        escapeText(
            question.prompt
        );

    const help =
        document.createElement(
            "p"
        );

    help.className =
        "question-help";

    help.textContent =
        escapeText(
            question.help_text
        );

    const options =
        document.createElement(
            "div"
        );

    options.className =
        "question-options";

    const inputName =
        `answer-${question.id}`;

    question.options.forEach(
        (option, index) => {
            const optionWrapper =
                document.createElement(
                    "div"
                );

            optionWrapper.className =
                "answer-option";

            const input =
                document.createElement(
                    "input"
                );

            input.type = "radio";

            input.name =
                inputName;

            input.value =
                String(
                    option
                );

            input.id =
                `${inputName}-${index}`;

            input.dataset.questionId =
                question.id;

            const label =
                document.createElement(
                    "label"
                );

            label.htmlFor =
                input.id;

            label.textContent =
                String(option);

            optionWrapper.appendChild(
                input
            );

            optionWrapper.appendChild(
                label
            );

            options.appendChild(
                optionWrapper
            );
        }
    );

    wrapper.appendChild(number);
    wrapper.appendChild(questionText);
    wrapper.appendChild(help);
    wrapper.appendChild(options);

    return wrapper;
}


function getAnsweredResponses() {
    const responses = {};

    document
        .querySelectorAll(
            ".question-item"
        )
        .forEach(
            (item) => {
                const checked =
                    item.querySelector(
                        "input[type='radio']:checked"
                    );

                if (checked) {
                    responses[
                        checked.dataset.questionId
                    ] = checked.value;
                }
            }
        );

    return responses;
}


function updateProgress() {
    const responses =
        getAnsweredResponses();

    const answeredCount =
        Object.keys(
            responses
        ).length;

    const total =
        questionnaire.length || 50;

    const percentage =
        Math.round(
            (answeredCount / total) *
                100
        );

    const countElement =
        assessmentElement(
            "assessment-progress-count"
        );

    const percentElement =
        assessmentElement(
            "assessment-progress-percent"
        );

    const barElement =
        assessmentElement(
            "assessment-progress-bar"
        );

    const messageElement =
        assessmentElement(
            "assessment-progress-message"
        );

    if (countElement) {
        countElement.textContent =
            `${answeredCount} / ${total}`;
    }

    if (percentElement) {
        percentElement.textContent =
            `${percentage}%`;
    }

    if (barElement) {
        barElement.style.width =
            `${percentage}%`;
    }

    if (messageElement) {
        if (answeredCount === total) {
            messageElement.textContent =
                "All questions answered. You can submit the assessment.";
        } else {
            messageElement.textContent =
                `${total - answeredCount} question(s) remaining.`;
        }
    }

    updateActiveCategory();

    return {
        answeredCount,
        total,
        percentage,
        responses,
    };
}


function attachAnswerListeners() {
    document
        .querySelectorAll(
            ".question-item input[type='radio']"
        )
        .forEach(
            (input) => {
                input.addEventListener(
                    "change",
                    () => {
                        const item =
                            input.closest(
                                ".question-item"
                            );

                        if (item) {
                            item.classList.remove(
                                "unanswered"
                            );
                        }

                        updateProgress();
                    }
                );
            }
        );
}


function updateActiveCategory() {
    const sections =
        [
            ...document.querySelectorAll(
                ".question-category"
            ),
        ];

    const buttons =
        [
            ...document.querySelectorAll(
                ".category-nav-button"
            ),
        ];

    if (
        sections.length === 0 ||
        buttons.length === 0
    ) {
        return;
    }

    let activeSection =
        sections[0];

    const viewportMarker =
        window.scrollY + 150;

    sections.forEach(
        (section) => {
            if (
                section.offsetTop <=
                viewportMarker
            ) {
                activeSection =
                    section;
            }
        }
    );

    buttons.forEach(
        (button) => {
            button.classList.toggle(
                "active",
                button.dataset.category ===
                    activeSection.id.replace(
                        "category-",
                        ""
                    )
            );
        }
    );
}


function findMissingQuestionIds() {
    const responses =
        getAnsweredResponses();

    return questionnaire
        .filter(
            (question) =>
                !responses[
                    question.id
                ]
        )
        .map(
            (question) =>
                question.id
        );
}


function markMissingQuestions(
    missingIds
) {
    document
        .querySelectorAll(
            ".question-item"
        )
        .forEach(
            (item) => {
                const questionId =
                    item.dataset.questionId;

                item.classList.toggle(
                    "unanswered",
                    missingIds.includes(
                        questionId
                    )
                );
            }
        );
}


function scrollToFirstMissingQuestion(
    missingIds
) {
    if (
        missingIds.length === 0
    ) {
        return;
    }

    const first =
        document.querySelector(
            `.question-item[data-question-id="${missingIds[0]}"]`
        );

    if (first) {
        first.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });
    }
}


function setSubmitState(
    isSubmitting
) {
    const button =
        assessmentElement(
            "submit-assessment"
        );

    if (!button) {
        return;
    }

    button.disabled =
        isSubmitting;

    button.textContent =
        isSubmitting
            ? "Calculating..."
            : "Calculate privacy risk";
}


function createTextElement(
    tagName,
    className,
    text
) {
    const element =
        document.createElement(
            tagName
        );

    if (className) {
        element.className =
            className;
    }

    element.textContent =
        escapeText(text);

    return element;
}


function renderCategoryResults(
    categoryScores
) {
    const container =
        assessmentElement(
            "result-category-grid"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    Object.entries(
        categoryScores
    )
        .sort(
            ([, first], [, second]) =>
                Number(second) -
                Number(first)
        )
        .forEach(
            ([category, score]) => {
                const card =
                    document.createElement(
                        "article"
                    );

                card.className =
                    "result-category-card";

                const top =
                    document.createElement(
                        "div"
                    );

                top.className =
                    "result-category-top";

                const name =
                    createTextElement(
                        "span",
                        "result-category-name",
                        humanizeCategory(
                            category
                        )
                    );

                const scoreElement =
                    createTextElement(
                        "span",
                        "result-category-score",
                        formatScore(score)
                    );

                top.appendChild(name);
                top.appendChild(
                    scoreElement
                );

                const track =
                    document.createElement(
                        "div"
                    );

                track.className =
                    "result-category-track";

                const fill =
                    document.createElement(
                        "div"
                    );

                fill.className =
                    "result-category-fill";

                fill.style.width =
                    `${Math.min(
                        100,
                        Math.max(
                            0,
                            Number(score)
                        )
                    )}%`;

                track.appendChild(fill);

                card.appendChild(top);
                card.appendChild(track);

                container.appendChild(
                    card
                );
            }
        );
}


function renderFindings(
    findings
) {
    const container =
        assessmentElement(
            "result-findings"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (
        !Array.isArray(findings) ||
        findings.length === 0
    ) {
        container.appendChild(
            createTextElement(
                "div",
                "result-list-empty",
                "No problem findings were generated for this assessment."
            )
        );

        return;
    }

    findings.forEach(
        (finding) => {
            const item =
                document.createElement(
                    "article"
                );

            item.className =
                "result-list-item";

            const top =
                document.createElement(
                    "div"
                );

            top.className =
                "result-list-item-top";

            const title =
                createTextElement(
                    "h5",
                    "",
                    finding.title ||
                        humanizeCategory(
                            finding.category
                        )
                );

            const badge =
                createTextElement(
                    "span",
                    "result-badge",
                    finding.severity
                );

            top.appendChild(title);
            top.appendChild(badge);

            const description =
                createTextElement(
                    "p",
                    "",
                    finding.description
                );

            item.appendChild(top);
            item.appendChild(
                description
            );

            container.appendChild(
                item
            );
        }
    );
}


function renderRecommendations(
    recommendations
) {
    const container =
        assessmentElement(
            "result-recommendations"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (
        !Array.isArray(
            recommendations
        ) ||
        recommendations.length === 0
    ) {
        container.appendChild(
            createTextElement(
                "div",
                "result-list-empty",
                "No additional recommendations were generated."
            )
        );

        return;
    }

    recommendations.forEach(
        (recommendation) => {
            const item =
                document.createElement(
                    "article"
                );

            item.className =
                "result-list-item";

            const top =
                document.createElement(
                    "div"
                );

            top.className =
                "result-list-item-top";

            const title =
                createTextElement(
                    "h5",
                    "",
                    humanizeCategory(
                        recommendation.category ||
                            recommendation.finding_type
                    )
                );

            const badge =
                createTextElement(
                    "span",
                    "result-badge",
                    recommendation.priority
                );

            top.appendChild(title);
            top.appendChild(badge);

            const text =
                createTextElement(
                    "p",
                    "",
                    recommendation.recommendation
                );

            item.appendChild(top);
            item.appendChild(text);

            container.appendChild(
                item
            );
        }
    );
}


function renderAssessmentResult(
    assessment
) {
    latestAssessment =
        assessment;

    const score =
        Number(
            assessment.overall_score
        );

    const scoreElement =
        assessmentElement(
            "result-score"
        );

    const riskElement =
        assessmentElement(
            "result-risk-level"
        );

    const descriptionElement =
        assessmentElement(
            "result-risk-description"
        );

    const findingCountElement =
        assessmentElement(
            "result-finding-count"
        );

    const recommendationCountElement =
        assessmentElement(
            "result-recommendation-count"
        );

    const assessmentIdElement =
        assessmentElement(
            "result-assessment-id"
        );

    if (scoreElement) {
        scoreElement.textContent =
            formatScore(score);
    }

    if (riskElement) {
        riskElement.className =
            `result-risk-level ${riskLevelClass(
                assessment.risk_level
            )}`;

        riskElement.textContent =
            assessment.risk_level;
    }

    if (descriptionElement) {
        descriptionElement.textContent =
            assessment.risk_description;
    }

    if (findingCountElement) {
        findingCountElement.textContent =
            String(
                assessment.findings
                    ?.length || 0
            );
    }

    if (recommendationCountElement) {
        recommendationCountElement.textContent =
            String(
                assessment.recommendations
                    ?.length || 0
            );
    }

    if (assessmentIdElement) {
        assessmentIdElement.textContent =
            assessment.assessment_id;
    }

    renderCategoryResults(
        assessment.category_scores
    );

    renderFindings(
        assessment.findings
    );

    renderRecommendations(
        assessment.recommendations
    );

    const resultSection =
        assessmentElement(
            "assessment-result"
        );

    const form =
        assessmentElement(
            "assessment-form"
        );

    if (form) {
        form.hidden = true;
    }

    if (resultSection) {
        resultSection.hidden = false;

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    }
}


async function submitAssessment(
    event
) {
    event.preventDefault();

    setAssessmentError("");

    const missingIds =
        findMissingQuestionIds();

    if (
        missingIds.length > 0
    ) {
        markMissingQuestions(
            missingIds
        );

        setAssessmentError(
            `Please answer all questions before submitting. ${missingIds.length} question(s) are still unanswered.`
        );

        scrollToFirstMissingQuestion(
            missingIds
        );

        return;
    }

    const responses =
        getAnsweredResponses();

    setSubmitState(true);

    try {
        const data =
            await assessmentFetchJson(
                "/api/assessment",
                {
                    method: "POST",
                    body: JSON.stringify(
                        {
                            responses,
                        }
                    ),
                }
            );

        if (
            data.success !== true ||
            !data.assessment
        ) {
            throw new Error(
                "Assessment API returned an unexpected response."
            );
        }

        renderAssessmentResult(
            data.assessment
        );

        updateProgress();
    } catch (error) {
        setAssessmentError(
            error.message ||
                "The assessment could not be submitted."
        );
    } finally {
        setSubmitState(false);
    }
}


function resetAssessment() {
    latestAssessment = null;

    const form =
        assessmentElement(
            "assessment-form"
        );

    const result =
        assessmentElement(
            "assessment-result"
        );

    if (form) {
        form.hidden = false;

        form.reset();
    }

    if (result) {
        result.hidden = true;
    }

    document
        .querySelectorAll(
            ".question-item.unanswered"
        )
        .forEach(
            (item) => {
                item.classList.remove(
                    "unanswered"
                );
            }
        );

    setAssessmentError("");

    updateProgress();

    const assessmentSection =
        assessmentElement(
            "assessment"
        );

    if (assessmentSection) {
        assessmentSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    }
}


async function initializeAssessment() {
    const loading =
        assessmentElement(
            "assessment-loading"
        );

    const form =
        assessmentElement(
            "assessment-form"
        );

    try {
        const data =
            await loadQuestionnaire();

        const groups =
            groupQuestionsByCategory(
                data.questions
            );

        renderCategoryNavigation(
            groups
        );

        renderQuestionnaire(
            data.questions
        );

        updateProgress();

        if (loading) {
            loading.hidden = true;
        }

        if (form) {
            form.hidden = false;
        }
    } catch (error) {
        if (loading) {
            loading.hidden = true;
        }

        setAssessmentError(
            error.message ||
                "The questionnaire could not be loaded."
        );
    }
}


function attachAssessmentEvents() {
    const form =
        assessmentElement(
            "assessment-form"
        );

    const retakeButton =
        assessmentElement(
            "retake-assessment"
        );

    if (form) {
        form.addEventListener(
            "submit",
            submitAssessment
        );
    }

    if (retakeButton) {
        retakeButton.addEventListener(
            "click",
            resetAssessment
        );
    }

    window.addEventListener(
        "scroll",
        updateActiveCategory,
        {
            passive: true,
        }
    );
}


document.addEventListener(
    "DOMContentLoaded",
    () => {
        attachAssessmentEvents();
        initializeAssessment();
    }
);