/**
 * Popup Response Handler
 * 
 * Manages communication between popup/modal windows and parent windows for model creation/editing.
 * Handles adding newly created or edited models back to select2 fields in the parent window.
 * 
 * Supports:
 * - Traditional Django admin popups (window.opener)
 * - Iframe-based modals (window.parent messaging)
 * - Nested popups (forwarding responses up the chain)
 */

// Patch Django admin scripts that fail in iframe context
// These scripts expect to be in a full window, not an iframe
if (window.self !== window.top) {
  // We're in an iframe - Django admin scripts may fail trying to access parent elements
  // Suppress errors from prepopulate_init.js and change_form.js in iframe context
  window.addEventListener('error', function(event) {
    // Log but don't propagate errors from Django admin scripts in iframe context
    if ((event.filename && event.filename.includes('prepopulate_init.js')) ||
        (event.filename && event.filename.includes('change_form.js'))) {
      console.log('Suppressed Django admin script error in iframe context:', event.message);
      return true; // Prevent error from propagating
    }
  }, true); // Use capture phase to catch errors before they propagate
}

(function() {
  'use strict';

  /**
   * Stores popup-related metadata from URL parameters and context
   */
  const PopupState = {
    toField: null,
    popupId: null,
    isPopup: false,
    isIframe: false,
    action: 'add', // 'add', 'change', or 'delete'
  };

  /**
   * Initialize popup state from URL parameters and Django's popup response data
   * Django sends _popup=1, _to_field=id, and _popup_id=<id> parameters
   */
  function initializePopupState() {
    const params = new URLSearchParams(window.location.search);
    
    PopupState.toField = params.get('_to_field') || 'id';
    PopupState.popupId = params.get('_popup_id');
    
    // Detect if we're in an iframe by checking window references
    PopupState.isIframe = window.self !== window.top;
    
    // If we're in an iframe, we're NOT a traditional popup window (even if _popup=1)
    // Iframes have their own response mechanism via window.parent
    if (PopupState.isIframe) {
      PopupState.isPopup = false;
    } else {
      PopupState.isPopup = params.get('_popup') === '1' || params.get('_popup') === 'true';
    }
    
    // Try to get action from Django's popup response constants
    const popupConstantsElement = document.getElementById('django-admin-popup-response-constants');
    if (popupConstantsElement) {
      try {
        const initData = JSON.parse(popupConstantsElement.dataset.popupResponse);
        PopupState.action = initData.action || 'add';
      } catch (e) {
        console.log('Could not parse Django popup response constants');
      }
    }
    
    console.log('Popup State Initialized:', PopupState);
  }

  /**
   * Get the value to send to parent window (usually the object ID)
   * Extracts the ID from the current form's hidden input field
   */
  function getPopupValue() {
    const idInput = document.querySelector('input[name="id"]');
    if (idInput && idInput.value) {
      return idInput.value;
    }
    
    // Fallback: try to get from Django's popup response constants
    const popupConstantsElement = document.getElementById('django-admin-popup-response-constants');
    if (popupConstantsElement) {
      try {
        const initData = JSON.parse(popupConstantsElement.dataset.popupResponse);
        return initData.value || initData.pk || '';
      } catch (e) {
        // Silently fail
      }
    }
    
    return '';
  }

  /**
   * Get the display label for the object
   * Tries multiple methods to extract a meaningful label
   */
  function getPopupLabel() {
    // Try Django's popup response constants first
    const popupConstantsElement = document.getElementById('django-admin-popup-response-constants');
    if (popupConstantsElement) {
      try {
        const initData = JSON.parse(popupConstantsElement.dataset.popupResponse);
        if (initData.obj) {
          return initData.obj;
        }
      } catch (e) {
        // Silently fail
      }
    }

    // Try to get from common name fields in forms (in order of preference)
    const nameFields = [
      'input[name="name"]',
      'input[name="title"]', 
      'input[name="label"]',
      'textarea[name="name"]',
      'textarea[name="title"]',
      'input[type="text"]:not([type="hidden"]):not([name="id"])'
    ];
    
    for (const selector of nameFields) {
      const field = document.querySelector(selector);
      if (field && field.value && field.value.trim()) {
        console.log(`Found label from field '${field.name}':`, field.value);
        return field.value.trim();
      }
    }
    
    // Try to get from page title
    const titleElement = document.querySelector('h1, h2, .page-title');
    if (titleElement) {
      const text = titleElement.textContent.trim();
      // Remove "Add" or "Change" prefix if present
      const cleaned = text.replace(/^(Add|Change|Edit)\s+/i, '').trim();
      if (cleaned) {
        console.log('Found label from page title:', cleaned);
        return cleaned;
      }
    }
    
    // Fallback: if all else fails, return empty string (will use ID as fallback in dismissAddRelatedModal)
    console.log('Could not extract label for object');
    return '';
  }

  /**
   * Send response back to parent window or iframe parent
   * This is called after successful form submission in popup mode
   */
  function sendPopupResponse(objectId, objectLabel) {
    if (!objectId) {
      console.warn('Cannot send popup response: no object ID provided');
      return;
    }

    const response = {
      pk: objectId,
      obj: objectLabel || objectId,
      id: objectId,
      label: objectLabel || objectId,
      new_value: objectId, // For Django's expected format
    };

    console.log('Sending popup response:', response);

    if (PopupState.isIframe && window.parent && window.parent !== window.self) {
      // For iframe: send via postMessage or parent's function
      if (typeof window.parent.dismissAddRelatedModal === 'function') {
        // Palette Admin iframe modal handler
        window.parent.dismissAddRelatedModal(objectId, objectLabel || objectId);
        console.log('Popup response sent to parent iframe via dismissAddRelatedModal');
        return;
      } else if (typeof window.parent.postMessage === 'function') {
        // Send via postMessage for other iframe setups
        window.parent.postMessage({
          type: 'popup_response',
          pk: objectId,
          obj: objectLabel || objectId,
          action: PopupState.action,
        }, window.location.origin);
        console.log('Popup response sent to parent via postMessage');
        return;
      }
    }
    
    if (PopupState.isPopup && window.opener) {
      // For traditional popup: use Django's expected functions
      try {
        if (window.opener && typeof window.opener.dismissAddRelatedObjectPopup === 'function') {
          window.opener.dismissAddRelatedObjectPopup(window, response.pk, response.obj);
          console.log('Popup response sent via dismissAddRelatedObjectPopup');
        } else if (window.opener && typeof window.opener.dismissChangeRelatedObjectPopup === 'function' && PopupState.action === 'change') {
          window.opener.dismissChangeRelatedObjectPopup(window, response.pk, response.obj, response.new_value);
          console.log('Popup response sent via dismissChangeRelatedObjectPopup');
        } else if (window.opener && typeof window.opener.dismissPopup === 'function') {
          // Fallback to custom dismissPopup
          window.opener.dismissPopup(response.pk, response.obj);
          console.log('Popup response sent via dismissPopup');
        } else {
          console.warn('No popup handler function found on window.opener');
        }
        
        // Close the popup window after a brief delay to ensure response is processed
        setTimeout(() => {
          console.log('Closing popup window');
          window.close();
        }, 200);
      } catch (e) {
        console.error('Error sending popup response:', e);
      }
    }
  }

  /**
   * Handle form submission in popup mode
   * Intercepts form submission to capture the response before page reload
   */
  function setupFormSubmissionHandler() {
    const form = document.querySelector('form');
    if (!form) return;

    // Use capture phase to run before Django's form submission
    form.addEventListener(
      'submit',
      function(e) {
        // Only handle if this is a popup/iframe context
        if (!PopupState.isPopup && !PopupState.isIframe) {
          return;
        }

        console.log('Form submitted in popup context, action:', PopupState.action);

        // Store values before form submission
        const objectId = getPopupValue();
        const objectLabel = getPopupLabel();

        // Let the form submit normally, but prepare to send response
        // Delay to ensure form is processed and response data is available
        setTimeout(() => {
          // Re-fetch in case values changed after form submission
          const finalId = getPopupValue() || objectId;
          const finalLabel = getPopupLabel() || objectLabel;
          
          if (finalId) {
            sendPopupResponse(finalId, finalLabel);
          }
        }, 200);
      },
      true
    );
  }

  /**
   * Handle beforeunload event to send response when popup closes
   * Fallback mechanism if form submission doesn't trigger response
   */
  function setupBeforeUnloadHandler() {
    window.addEventListener('beforeunload', function(e) {
      // Only handle if this is a popup/iframe context
      if (!PopupState.isPopup && !PopupState.isIframe) {
        return;
      }

      const objectId = getPopupValue();
      if (objectId) {
        const objectLabel = getPopupLabel();
        console.log('Popup unloading, sending final response:', { objectId, objectLabel });
        sendPopupResponse(objectId, objectLabel);
      }
    });
  }

  /**
   * Handle messages from child iframes (for nested popups)
   * Allows popups within popups to work correctly
   */
  function setupMessageHandler() {
    window.addEventListener('message', function(event) {
      // Only accept messages from same origin
      if (event.origin !== window.location.origin) {
        console.warn('Rejecting message from different origin:', event.origin);
        return;
      }

      // Handle popup response message from child iframe
      if (event.data && event.data.type === 'popup_response') {
        console.log('Received popup response message from child:', event.data);
        const { pk, obj } = event.data;
        
        // If we're also in a popup/iframe, forward the message up
        if ((PopupState.isPopup || PopupState.isIframe) && pk) {
          sendPopupResponse(pk, obj);
        }
      }
    });
  }

  /**
   * Global function for parent windows to handle popup responses
   * Called by child popups/iframes to notify parent of new/edited model
   * Compatible with Django's admin popup system
   */
  window.dismissPopup = function(pk, obj) {
    console.log('dismissPopup called with:', { pk, obj });
    // Default handler - can be overridden by parent window
    if (window.parent && window.parent.dismissPopup && window.parent !== window) {
      window.parent.dismissPopup(pk, obj);
    }
  };

  /**
   * Global function for parent windows to handle related modal responses
   * Called by child iframes in modals to notify parent of new/edited model
   * Specific to Palette Admin's select2 modal system
   */
  window.dismissAddRelatedModal = function(pk, obj) {
    console.log('dismissAddRelatedModal called with:', { pk, obj });
    // Default handler - will be overridden by change_form.html JavaScript
    // This just prevents errors if called before the full script loads
  };

  /**
   * Django admin compatible handlers
   * For traditional popup workflow
   */
  window.dismissAddRelatedObjectPopup = function(win, objId, objStr) {
    console.log('dismissAddRelatedObjectPopup (Django compat) called with:', { objId, objStr });
    if (window.parent && window.parent !== window) {
      window.parent.dismissAddRelatedModal(objId, objStr);
    }
  };

  window.dismissChangeRelatedObjectPopup = function(win, objId, objStr, newId) {
    console.log('dismissChangeRelatedObjectPopup (Django compat) called with:', { objId, objStr, newId });
    if (window.parent && window.parent !== window) {
      window.parent.dismissAddRelatedModal(newId || objId, objStr);
    }
  };

  /**
   * Export functions for external use
   */
  window.PopupResponse = {
    initialize: initializePopupState,
    getPopupValue: getPopupValue,
    getPopupLabel: getPopupLabel,
    send: sendPopupResponse,
    state: PopupState,
  };

  /**
   * Initialize when DOM is ready
   */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initializePopupState();
      setupFormSubmissionHandler();
      setupBeforeUnloadHandler();
      setupMessageHandler();
      console.log('Popup Response Handler initialized');
    });
  } else {
    // DOM already loaded
    initializePopupState();
    setupFormSubmissionHandler();
    setupBeforeUnloadHandler();
    setupMessageHandler();
    console.log('Popup Response Handler initialized');
  }
})();
