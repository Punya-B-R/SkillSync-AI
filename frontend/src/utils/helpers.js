/**
 * Utility helper functions.
 */

/**
 * Format date string.
 * @param {string} dateString - Date string
 * @returns {string} Formatted date
 */
export const formatDate = (dateString) => {
  // TODO: Implement date formatting
  return dateString
}

/**
 * Validate file type.
 * @param {File} file - File object
 * @param {Array} allowedTypes - Allowed file types
 * @returns {boolean} True if valid
 */
export const validateFileType = (file, allowedTypes = ['pdf', 'docx']) => {
  // TODO: Check file extension against allowed types
  // TODO: Return true/false
  const extension = file.name.split('.').pop().toLowerCase()
  return allowedTypes.includes(extension)
}

/**
 * Format file size.
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
export const formatFileSize = (bytes) => {
  // TODO: Convert bytes to human-readable format (KB, MB)
  // TODO: Return formatted string
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

