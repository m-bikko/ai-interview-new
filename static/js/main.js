/* Main JavaScript for AI Interview Platform */

$(document).ready(function() {
    // Sidebar toggle
    $('#sidebarCollapse').on('click', function() {
        $('.sidebar').toggleClass('active');
        $('.content').toggleClass('active');
    });

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

// Audio recording functionality for interviews
let recorder;
let audio_stream;
let audio_chunks = [];
let isRecording = false;
let recordingTimer;
let recordingSeconds = 0;
let maxRecordingSeconds = 120; // 2 minutes

// Start recording function
function startRecording(questionId) {
    // Reset the audio chunks array and timer
    audio_chunks = [];
    recordingSeconds = 0;
    
    // Update UI
    $(`#record-btn-${questionId}`).addClass('recording');
    $(`#record-status-${questionId}`).text('Recording...');
    $(`#recording-timer-${questionId}`).show();
    $(`#timer-${questionId}`).text('0:00');
    
    // Start timer
    recordingTimer = setInterval(function() {
        recordingSeconds++;
        const minutes = Math.floor(recordingSeconds / 60);
        const seconds = recordingSeconds % 60;
        $(`#timer-${questionId}`).text(`${minutes}:${seconds.toString().padStart(2, '0')}`);
        
        // Auto-stop at max time
        if (recordingSeconds >= maxRecordingSeconds) {
            stopRecording(questionId);
        }
    }, 1000);
    
    // Get user media
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            audio_stream = stream;
            recorder = new MediaRecorder(stream);
            
            // Listen for dataavailable event to collect audio chunks
            recorder.addEventListener('dataavailable', function(e) {
                audio_chunks.push(e.data);
            });
            
            // Listen for stop event to create the final blob and upload
            recorder.addEventListener('stop', function() {
                const audio_blob = new Blob(audio_chunks, { type: 'audio/webm' });
                uploadAudio(audio_blob, questionId);
            });
            
            // Start recording with a timeslice of 1000ms so we get regular data chunks
            recorder.start(1000);
            isRecording = true;
        })
        .catch(function(err) {
            console.error('Error starting recording:', err);
            alert('Could not access microphone. Please make sure it is connected and you have granted permission.');
            $(`#record-btn-${questionId}`).removeClass('recording');
            $(`#record-status-${questionId}`).text('Error: Could not access microphone');
        });
}

// Stop recording function
function stopRecording(questionId) {
    if (recorder && isRecording) {
        // Update UI
        $(`#record-btn-${questionId}`).removeClass('recording');
        $(`#record-status-${questionId}`).text('Processing...');
        $(`#recording-timer-${questionId}`).hide();
        
        // Stop the timer
        clearInterval(recordingTimer);
        
        // Stop the recorder
        recorder.stop();
        isRecording = false;
        
        // Stop all tracks from the stream
        if (audio_stream) {
            audio_stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Toggle recording function
function toggleRecording(questionId) {
    if (!isRecording) {
        startRecording(questionId);
    } else {
        stopRecording(questionId);
    }
}

// Upload audio function
function uploadAudio(blob, questionId) {
    const interviewId = $('#interview-id').val();
    
    // Create form data
    const formData = new FormData();
    formData.append('audio', blob, 'answer.webm');
    formData.append('interview_id', interviewId);
    formData.append('question_id', questionId);
    
    // Update UI
    $(`#record-status-${questionId}`).text('Uploading and analyzing...');
    
    // Send to server
    $.ajax({
        url: '/interviews/save-answer',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                // Update UI
                $(`#record-status-${questionId}`).text('Analysis complete!');
                $(`#feedback-${questionId}`).html(response.feedback.replace(/\n/g, '<br>'));
                $(`#question-box-${questionId}`).addClass('bg-light');
                $(`#question-box-${questionId} .record-controls`).hide();
                $(`#feedback-section-${questionId}`).removeClass('d-none');
                
                // Check if all questions have been answered
                const answeredQuestions = $('.feedback-section:not(.d-none)').length;
                const totalQuestions = $('.question-box').length;
                
                if (answeredQuestions === totalQuestions) {
                    $('#complete-interview-section').removeClass('d-none');
                }
            } else {
                $(`#record-status-${questionId}`).text('Error: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            $(`#record-status-${questionId}`).text('Error uploading audio');
            console.error('Error uploading audio:', error);
        }
    });
}

// Function to navigate to next question
function nextQuestion(currentQuestionId, nextQuestionId) {
    // Hide current question
    $(`#question-box-${currentQuestionId}`).addClass('d-none');
    
    // Show next question
    $(`#question-box-${nextQuestionId}`).removeClass('d-none');
    
    // If this is the last question, show the complete button
    const currentIndex = $(`#question-box-${nextQuestionId}`).data('index');
    const totalQuestions = $('.question-box').length;
    
    if (currentIndex === totalQuestions) {
        $('#complete-interview-section').removeClass('d-none');
    }
}

// Function to complete the interview
function completeInterview() {
    const interviewId = $('#interview-id').val();
    
    // Update UI
    $('#complete-btn').prop('disabled', true);
    $('#complete-btn').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...');
    
    // Send to server
    $.ajax({
        url: `/interviews/complete/${interviewId}`,
        type: 'POST',
        success: function(response) {
            window.location.href = `/interviews/review/${interviewId}`;
        },
        error: function(xhr, status, error) {
            $('#complete-btn').prop('disabled', false);
            $('#complete-btn').text('Complete Interview');
            alert('Error completing interview. Please try again.');
            console.error('Error completing interview:', error);
        }
    });
}